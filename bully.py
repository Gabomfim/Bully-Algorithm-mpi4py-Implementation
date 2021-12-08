#When a process P recovers from failure, or the failure detector indicates that the current coordinator has failed, P performs the following actions:

#1 - If P has the highest process ID, it sends a Victory message to all other processes and becomes the new Coordinator. Otherwise, P broadcasts an Election message to all other processes with higher process IDs than itself.
#2 - If P receives no Answer after sending an Election message, then it broadcasts a Victory message to all other processes and becomes the Coordinator.
#3 - If P receives an Answer from a process with a higher ID, it sends no further messages for this election and waits for a Victory message. (If there is no Victory message after a period of time, it restarts the process at the beginning.)
#4 - If P receives an Election message from another process with a lower ID it sends an Answer message back and starts the election process at the beginning, by sending an Election message to higher-numbered processes.
#5 - If P receives a Coordinator message, it treats the sender as the coordinator.

from mpi4py import MPI
import time

comm = MPI.COMM_WORLD

my_rank = comm.Get_rank()
p = comm.Get_size()
    
electionCaller = 0

def baseCase():
    for procid in range(0, p):
        imposingMessage = str(procid) + " acknowledges that " + str(my_rank) + " is the leader"
        comm.isend(imposingMessage, dest=procid)
    print(comm.irecv(source=my_rank).wait())

if my_rank == electionCaller:
    reqList = []
    for procid in range(my_rank+1, p):
        message = "Hello from " + str(my_rank)
        comm.isend(message, dest=procid)
        reqList.append(comm.irecv(source=procid))
    time.sleep(0.1)
    status = MPI.Status()
    leader = None
    print("BLARG: ", MPI.Request.testany(reqList, status))
    if MPI.Request.testany(reqList, status)[1]: #If there was a response, I am not the leader
        leader = comm.irecv(source=MPI.ANY_SOURCE) #The leader will be announced through this request
        print(leader)
    else:
        baseCase()
    while(True):
        if(leader):
            leaderStatus = MPI.Status()
            leaderStatus = MPI.Request.test(leader, leaderStatus)
            print(leaderStatus[1])
else:
    req = comm.irecv(source=MPI.ANY_SOURCE)
    status = MPI.Status()
    req.wait(status)
    message = "ACK from " + str(my_rank)
    comm.isend(message, dest=status.Get_source())
    if my_rank == 3:
        baseCase()



'''def callElection():
    reqList = []
    for procid in range(my_rank, p):
        message = my_rank
        comm.isend(message, dest=procid)
        reqList = comm.irecv(source=procid)
    time.sleep(0.2)
    #for req in reqList:
    #    req.cancel()
    if MPI.Request.testany([reqList]):
        #I am not the leader, wait for the broadcast
        leader = None
        reqBroadcast = comm.Ibcast(leader, root=MPI.ANY_SOURCE)

    else:
        #Broadcast that I am the leader
        leader = str(my_rank) + " is the leader"
        reqBroadcast = comm.Ibcast(leader, root=my_rank)
        return reqBroadcast


if my_rank == electionCaller:
    callElection()

else:
    reqBroadcastList = []
    req = comm.irecv(source=MPI.ANY_SOURCE)
    while True:
        if req.test():
            status = MPI.Status()
            req.wait(status)
            ack = "ACK from process " + str(my_rank)
            comm.isend(ack, dest=status.Get_source())
            #Continue Election
            reqBroadcastList += callElection()
            req = comm.irecv(source=MPI.ANY_SOURCE)
        if MPI.Request.testany(reqBroadcastList): #wait for the leader announcement
            leader = MPI.Request.testany(reqBroadcastList)
            print(leader)'''