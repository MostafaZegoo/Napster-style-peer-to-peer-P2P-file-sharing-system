Purpose: first to get you familiarize with sockets/RPCs/RMIs, processes, threads; second to learn the design and internals of a Napster-style peer-to-peer (P2P) file sharing system.

You need to design a simple P2P system that has two components: 

                           1. A central indexing server. This server indexes the contents of all of the peers that register with it. It also provides search facility to peers. In our simple version, you don't need to implement sophisticated searching algorithms; an exact match will be fine.  Minimally, the server should provide the following interface to the peer clients:  
              • registry (peer id, file name, ...) -- invoked by a peer to register all its files with the indexing server. The server then builds the index for the peer. Other sophisticated algorithms such as automatic indexing are not required, but feel free to do whatever is reasonable. You may provide optional information to the server to make it more 'real', such as the clients’ bandwidth, etc.  
              • search (file name) -- this procedure should search the index and return all the matching peers to the requestor.   
              
                           2. A peer. A peer is both a client and a server. As a client, the user specifies a file name with the indexing server using "lookup". The indexing server returns a list of all other peers that hold the file. The user can pick one such peer and the client then connects to this peer and downloads the file. As a server, the peer waits for requests from other peers and sends the requested file when receiving a request.  Minimally, the peer server should provide the following interface to the peer client:  
              • obtain (file name) -- invoked by a peer to download a file from another peer.   
                           
Both the indexing server and a peer server should be able to accept multiple client requests at the same time. This could be easily done using threads. Be aware of the thread synchronizing issues to avoid inconsistency or deadlock in your system.
