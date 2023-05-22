package reverseproxy

import "net"

type Listener struct {
	Addr    string
	TLSCert string
	TLSKey  string
}

func (l *Listener) Make() (net.Listener, error) {
	return net.Listen("tcp", l.Addr)
}

func (l *Listener) ServesTLS() bool {
	return len(l.TLSCert) > 0 && len(l.TLSKey) > 0
}
