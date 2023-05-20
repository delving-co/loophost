package main

import (
	"encoding/json"
	"fmt"
	"log"
	"os"
	"os/signal"

	"github.com/10in30/loophost/reverseproxy"
	"github.com/fsnotify/fsnotify"
	"github.com/gorilla/mux"
)

var path = os.Getenv("LOOPHOST_DATA_PATH")

func check(e error) {
	if e != nil {
		panic(e)
	}
}

type Loopdata struct {
	Apps map[string]string `json:"apps"`
	Fqdn string            `json:"fqdn"`
}

func loadRoutes(r *reverseproxy.ReverseProxy) {
	fmt.Println("Loading routes from json")

	r.ClearTargets()
	dat, err := os.ReadFile(path + "/loophost.json")
	check(err)
	var defn Loopdata
	err = json.Unmarshal(dat, &defn)
	check(err)
	for k := range defn.Apps {
		a := mux.NewRouter()
		host := k + "." + defn.Fqdn
		fmt.Println(host)
		fmt.Println(defn.Apps[k])
		a.Host(host)
		r.AddTarget([]string{defn.Apps[k]}, a)
	}

	// Handle anything else
	r.AddTarget([]string{path + "/loophost.soc"}, nil)

}

func main() {

	dat, err := os.ReadFile(path + "/loophost.json")
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
		r := &reverseproxy.ReverseProxy{}
		// Listen for http://
		r.AddListener(":80")
		// Listen for https://
		r.AddListenerTLS(":443",
			path+"/live/"+defn.Fqdn+"/fullchain.pem",
			path+"/live/"+defn.Fqdn+"/privkey.pem")
		if err := r.Start(); err != nil {
			log.Fatal(err)
		}
	serving:
		for {
			select {
			case sig := <-hup:
				if sig == 0 {
					loadRoutes(r)

				} else {
					break serving
				}

			case event, ok := <-watcher.Events:
				if !ok {
					return
				}
				log.Println("event:", event)
				if event.Has(fsnotify.Write) {
					log.Println("modified file:", event.Name)
				}

				go func() { hup <- 0 }()

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
	p := os.Getenv("LOOPHOST_DATA_PATH")
	err = watcher.Add(p)
	if err != nil {
		log.Fatal(err)
	}

	hup <- 0

	// Block until we receive our signal.

	<-c
	hup <- 1
}
