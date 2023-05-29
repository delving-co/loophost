package main

import (
	"encoding/json"
	"log"
	"os"
	"os/signal"
	"path/filepath"
	"strings"

	"github.com/delving-co/loophost/loopproxy/reverseproxy"
	"github.com/fsnotify/fsnotify"
	"github.com/gorilla/mux"
)

var path = os.Args[1]

func check(e error) {
	if e != nil {
		panic(e)
	}
}

type Loopdata struct {
	Apps   map[string]string `json:"apps"`
	Fqdn   string            `json:"fqdn"`
	Tunnel string            `json:"tunnel"`
}

func loadRoutes(r *reverseproxy.ReverseProxy) {
	log.Println("Loading routes from json")

	r.ClearTargets()
	dat, err := os.ReadFile(filepath.FromSlash(path + "/loophost.json"))
	check(err)
	var defn Loopdata
	err = json.Unmarshal(dat, &defn)
	check(err)
	domains := []string{defn.Fqdn, defn.Tunnel}
	for k := range defn.Apps {
		for _, subdomain := range domains {
			a := mux.NewRouter()
			host := k + "." + subdomain
			log.Println(host)
			log.Println(defn.Apps[k])
			a.Host(host)
			r.AddTarget([]string{defn.Apps[k]}, a)
		}
	}

	// Handle anything else
	r.AddTarget([]string{"http://127.0.0.1:5816"}, nil)

}

func main() {
	f, err := os.OpenFile(filepath.FromSlash(path+"/loophost-goproxy.log"), os.O_RDWR|os.O_CREATE|os.O_APPEND, 0666)
	if err != nil {
		log.Fatalf("error opening file: %v", err)
	}
	defer f.Close()

	log.SetOutput(f)
	log.Println("Starting loophost proxy")

	dat, err := os.ReadFile(filepath.FromSlash(path + "/loophost.json"))
	check(err)
	var defn Loopdata
	err = json.Unmarshal(dat, &defn)
	check(err)

	// Create new watcher.
	watcher, err := fsnotify.NewWatcher()
	if err != nil {
		log.Fatal(err)
	}
	defer watcher.Close()
	c := make(chan os.Signal, 1)
	// We'll accept graceful shutdowns when quit via SIGINT (Ctrl+C)
	// SIGKILL, SIGQUIT or SIGTERM (Ctrl+/) will not be caught.
	signal.Notify(c, os.Interrupt)

	hup := make(chan int)

	// Start listening for events.
	go func() {
		log.Println("In goroutine adding listeners...")
		r := &reverseproxy.ReverseProxy{}
		// Listen for http://
		// r.AddListener(":80")
		// Listen for https://
		r.AddListenerTLS(":443",
			path+"/live/"+defn.Fqdn+"/fullchain.pem",
			path+"/live/"+defn.Fqdn+"/privkey.pem")
		r.AddListenerTLS(":4433",
			path+"/live/"+defn.Fqdn+"/fullchain.pem",
			path+"/live/"+defn.Fqdn+"/privkey.pem")
		if err := r.Start(); err != nil {
			log.Fatal(err)
		}
	serving:
		for {
			select {
			case sig := <-hup:
				log.Println("Received HUP")
				if sig == 0 {
					loadRoutes(r)

				} else {
					break serving
				}

			case event, ok := <-watcher.Events:
				if !ok {
					return
				}
				if event.Has(fsnotify.Write) {
					if strings.HasSuffix(event.Name, "json") {
						log.Println("modified file:", event.Name)
						go func() { hup <- 0 }()
					}
				}

			case err, ok := <-watcher.Errors:
				if !ok {
					break serving
				}
				log.Println("error:", err)
				break serving
			}
		}
		// Graceful shutdown
		r.Stop()
	}()

	// Add a path.
	err = watcher.Add(filepath.FromSlash(path))
	if err != nil {
		log.Fatal(err)
	}

	hup <- 0

	// Block until we receive our signal.

	<-c
	hup <- 1
}
