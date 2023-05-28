package reverseproxy

import (
	"context"
	"errors"
	"log"
	"net"
	"net/http"
	"net/http/httputil"
	"net/url"
	"strings"
	"sync"
	"time"

	"github.com/gorilla/mux"
)

type ReverseProxy struct {
	listeners []Listener
	proxy     *httputil.ReverseProxy
	servers   []*http.Server
	targets   []*Target
}

func (r *ReverseProxy) ClearTargets() error {
	r.targets = nil
	return nil
}

// AddTarget adds an upstream server to use for a request that matches
// a given gorilla/mux Router. These are matched via Director function.
func (r *ReverseProxy) AddTarget(upstreams []string, router *mux.Router) error {
	var upstreamPool []*string
	for _, upstream := range upstreams {

		if router == nil {
			router = mux.NewRouter()
			router.PathPrefix("/")
		}

		upstreamPool = append(upstreamPool, &upstream)
	}

	r.targets = append(r.targets, &Target{
		router:    router,
		upstreams: upstreamPool,
	})

	r.proxy.Transport = &http.Transport{
		// MaxIdleConnsPerHost: 1,
		// MaxConnsPerHost:     1,
		DialContext: func(ctx context.Context, netwrk, addr string) (net.Conn, error) {
			a := &addr
			network := netwrk
			if strings.HasPrefix(addr, "/") {
				// a = upstreamPool[0]
				a = &strings.Split(addr, ":")[0]
				network = "unix"
			}
			dialer := net.Dialer{}
			return dialer.DialContext(ctx, network, *a)
		},
	}

	return nil
}

// AddListener adds a listener for non-TLS connections on the given address
func (r *ReverseProxy) AddListener(address string) {

	l := Listener{
		Addr: address,
	}

	r.listeners = append(r.listeners, l)
}

// AddListenerTLS adds a listener for TLS connections on the given address
func (r *ReverseProxy) AddListenerTLS(address, tlsCert, tlsKey string) {

	l := Listener{
		Addr:    address,
		TLSCert: tlsCert,
		TLSKey:  tlsKey,
	}

	r.listeners = append(r.listeners, l)
}

// Start will listen on configured listeners
func (r *ReverseProxy) Start() error {
	log.Println("Starting reverse proxy")
	r.proxy = &httputil.ReverseProxy{
		Director: r.Director(),
	}

	for _, l := range r.listeners {
		log.Println("Making listener for " + l.Addr)
		listener, err := l.Make()
		if err != nil {
			// todo: Close any listeners that
			//       were created successfully
			return err
		}

		srv := &http.Server{Handler: r.proxy}

		r.servers = append(r.servers, srv)

		// TODO: Handle unexpected errors from our servers
		if l.ServesTLS() {
			go func() {
				if err := srv.ServeTLS(listener, l.TLSCert, l.TLSKey); !errors.Is(err, http.ErrServerClosed) {
					log.Println(err)
				}
			}()
		} else {
			go func() {
				if err := srv.Serve(listener); !errors.Is(err, http.ErrServerClosed) {
					log.Println(err)
				}
			}()
		}
	}

	return nil
}

// Stop will gracefully shut down all listening servers
func (r *ReverseProxy) Stop() {
	ctx, cancel := context.WithTimeout(context.Background(), time.Second*10)
	defer cancel()

	var wg sync.WaitGroup

	for _, srv := range r.servers {
		srv := srv
		wg.Add(1)
		go func() {
			defer wg.Done()
			if err := srv.Shutdown(ctx); err != nil {
				log.Println(err)
			}
			log.Println("A listener was shutdown successfully")
		}()
	}

	// Wait for all servers to shut down
	wg.Wait()
	log.Println("Server shut down")
}

func ParseUpstream(r *ReverseProxy, upstream *string) (upstream_url url.URL) {
	upurl, err := url.Parse(*upstream)
	if err != nil {
		log.Println(err)
		panic(err)
	}
	upstream_url = url.URL(*upurl)
	if strings.HasPrefix(*upstream, "/") {
		upstream_url.Scheme = "http"
		upstream_url.Host = *upstream // "unix"
		upstream_url.Path = ""
		upstream_url.RawPath = ""
	}
	// fmt.Println(upstream_url)
	return
}

// Director returns a function for use in http.ReverseProxy.Director.
// The function matches the incoming request to a specific target and
// sets the request object to be sent to the matched upstream server.
func (r *ReverseProxy) Director() func(req *http.Request) {

	return func(req *http.Request) {
		for _, t := range r.targets {
			match := &mux.RouteMatch{}
			if t.router.Match(req, match) {
				upstream := t.SelectTarget()
				upstream_url := ParseUpstream(r, upstream)

				var targetQuery = upstream_url.RawQuery
				req.URL.Scheme = upstream_url.Scheme
				req.URL.Host = upstream_url.Host

				req.URL.Path, req.URL.RawPath = joinURLPath(&upstream_url, req.URL)
				if targetQuery == "" || req.URL.RawQuery == "" {
					req.URL.RawQuery = targetQuery + req.URL.RawQuery
				} else {
					req.URL.RawQuery = targetQuery + "&" + req.URL.RawQuery
				}
				if _, ok := req.Header["User-Agent"]; !ok {
					// explicitly disable User-Agent so it's not set to default value
					req.Header.Set("User-Agent", "")
				}
				// log.Println(req.URL.Path)
				break
			}
		}
	}
}

func singleJoiningSlash(a, b string) string {
	aslash := strings.HasSuffix(a, "/")
	bslash := strings.HasPrefix(b, "/")
	switch {
	case aslash && bslash:
		return a + b[1:]
	case !aslash && !bslash:
		return a + "/" + b
	}
	return a + b
}

func joinURLPath(a, b *url.URL) (path, rawpath string) {
	if a.RawPath == "" && b.RawPath == "" {
		return singleJoiningSlash(a.Path, b.Path), ""
	}
	// Same as singleJoiningSlash, but uses EscapedPath to determine
	// whether a slash should be added
	apath := a.EscapedPath()
	bpath := b.EscapedPath()

	aslash := strings.HasSuffix(apath, "/")
	bslash := strings.HasPrefix(bpath, "/")

	switch {
	case aslash && bslash:
		return a.Path + b.Path[1:], apath + bpath[1:]
	case !aslash && !bslash:
		return a.Path + "/" + b.Path, apath + "/" + bpath
	}
	return a.Path + b.Path, apath + bpath
}
