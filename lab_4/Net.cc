#ifndef NET
#define NET

#include <string.h>
#include <omnetpp.h>
#include <packet_m.h>

using namespace omnetpp;

class Net: public cSimpleModule {
private:

public:
    Net();
    virtual ~Net();
    int hopCountStats; // Variable to record hop count statistics
    int HopCount0; // Variable to find the hop count to the destination of the first runner
    int HopCount1; // Variable to find the hop count to the destination of the second runner

    int Gate; // Variable to determine which gate to send the packet to


protected:
    virtual void initialize();
    virtual void finish();
    virtual void handleMessage(cMessage *msg);
    void handleFirstRunnerPacket(Packet *pkt); // Function to handle the first runner packet
    void handleSecondRunnerPacket(Packet *pkt); // Function to handle the second runner packet
    void handleDataPacket(Packet *pkt); // Function to handle the data packet
};

Define_Module(Net);

#endif /* NET */

#define runner0 0
#define runner1 1
#define byteSize 2
#define destination 5
#define gateclockwise 0
#define gatecounterclockwise 1

Net::Net() {
}

Net::~Net() {
}

void Net::initialize() {
    hopCountStats = 0; // Initialize hop count statistics to 0

    HopCount0 = 0;  // Initialize hop count to destination of the first runner to 0
    HopCount1 = 0; // Initialize hop count to destination of the second runner to 0
    Gate = 0;  // Initialize the gate to 0

    // Create the first runner packet
    Packet *Runner0 = new Packet("Runner0",this->getParentModule()->getIndex());
    Runner0->setByteLength(byteSize);
    Runner0->setSource(this->getParentModule()->getIndex());
    Runner0->setDestination(destination);
    Runner0->setHopCount(0);
    Runner0->setHopCountToDestination(0);
    Runner0->setKind(runner0);
    
    // Create the second runner packet
    Packet *Runner1 = new Packet("Runner1",this->getParentModule()->getIndex());
    Runner1->setByteLength(byteSize);
    Runner1->setSource(this->getParentModule()->getIndex());
    Runner1->setDestination(destination);
    Runner1->setHopCount(0);
    Runner1->setHopCountToDestination(0);
    Runner1->setKind(runner1);

    // Send the runner packets to the link
    send(Runner0, "toLnk$o", gateclockwise);
    send(Runner1, "toLnk$o", gatecounterclockwise);
}

void Net::finish() {
    // Record hop count statistics
    recordScalar("Total hop count", hopCountStats);
}

void Net::handleFirstRunnerPacket(Packet *pkt) {
    // If the packet finishes the loop, delete it
    if (pkt->getSource() == this->getParentModule()->getIndex()) {
        HopCount0 = pkt->getHopCountToDestination();
        delete(pkt);
    }
    // send the packet to the next node
    else{
        // If the packet is the expected destination, save the hop count to the destination
        if (pkt->getDestination() == this->getParentModule()->getIndex()) {
            pkt->setHopCountToDestination(pkt->getHopCount());
        }
        pkt->setHopCount(pkt->getHopCount() + 1);
        send(pkt, "toLnk$o", gateclockwise);
    }
}

void Net::handleSecondRunnerPacket(Packet *pkt) {
    // If the packet finishes the loop, delete it
    if (pkt->getSource() == this->getParentModule()->getIndex()) {
        HopCount1 = pkt->getHopCountToDestination();
        delete(pkt);
    }
    // send the packet to the next node
    else{
        // If the packet is the expected destination, save the hop count to the destination
        if (pkt->getDestination() == this->getParentModule()->getIndex()) {
            pkt->setHopCountToDestination(pkt->getHopCount());
        }
        pkt->setHopCount(pkt->getHopCount() + 1);
        send(pkt, "toLnk$o", gatecounterclockwise);
    }
}

void Net::handleDataPacket(Packet *pkt) {
    // If this node is the final destination, send to App
    if (pkt->getDestination() == this->getParentModule()->getIndex()) {
        send(pkt, "toApp$o");
        // Update hop count statistics
        hopCountStats += pkt->getHopCount();
    }
    // If not, forward the packet to some else
    else {
        // Determine which gate to send the packet to
        if (HopCount0 > HopCount1) {
            Gate = 1;
        } 
        // Increment the hop count
        pkt->setHopCount(pkt->getHopCount() + 1);
        send (pkt, "toLnk$o", Gate);
    }
}

void Net::handleMessage(cMessage *msg) {
    Packet *pkt = (Packet *) msg;
    if (pkt->getKind() == runner0) {
        handleFirstRunnerPacket(pkt);
        }
        else if (pkt->getKind() == runner1) {
            handleSecondRunnerPacket(pkt);
        }
        else {
            handleDataPacket(pkt);
        }
    }