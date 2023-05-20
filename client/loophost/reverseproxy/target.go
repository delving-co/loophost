package reverseproxy

import (
	"sync"

	"github.com/gorilla/mux"
)

type Target struct {
	router       *mux.Router
	upstreams    []*string
	lastUpstream int
	lock         sync.Mutex
}

// SelectTarget will load balance amongst available
// targets using a round-robin algorithm
func (t *Target) SelectTarget() *string {
	count := len(t.upstreams)
	if count == 1 {
		return t.upstreams[0]
	}

	t.lock.Lock()
	defer t.lock.Unlock()

	next := t.lastUpstream + 1
	if next >= count {
		next = 0
	}

	t.lastUpstream = next

	return t.upstreams[next]
}
