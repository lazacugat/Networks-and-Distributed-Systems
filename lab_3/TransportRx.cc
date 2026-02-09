#ifndef TRANSPORTRX
#define TRANSPORTRX

#include <string.h>
#include <omnetpp.h>

using namespace omnetpp;
#include "FeedbackPkt_m.h"

class TransportRx: public cSimpleModule {
private:
    cQueue buffer;
    cQueue feedbackBuffer;
    cMessage *endServiceEvent;
    simtime_t serviceTime;

    int packetDrop;
    cOutVector packetDropVector;
    cOutVector bufferSizeVector;

public:
    TransportRx();
    virtual ~TransportRx();
protected:
    virtual void initialize();
    virtual void finish();
    virtual void handleMessage(cMessage *msg);
    virtual void createFeedback();
    virtual void enqueuePacket(cMessage *msg);
};

Define_Module(TransportRx);

TransportRx::TransportRx() {
    endServiceEvent = NULL;
}

TransportRx::~TransportRx() {
    cancelAndDelete(endServiceEvent);
}

void TransportRx::initialize() {
    buffer.setName("Receiver: Data buffer");
    endServiceEvent = new cMessage("endService");

    bufferSizeVector.setName("bufferSize");
    packetDropVector.setName("packetDrop");
    packetDrop = 0;
}

void TransportRx::finish() {
    recordScalar("Packets dropped", packetDrop);
    recordScalar("Final buffer size", buffer.getLength());
}


void TransportRx::handleMessage(cMessage *msg) {

    // if msg is signaling an endServiceEvent
    if (msg == endServiceEvent) {
        // if packet in buffer, send next one
        if (!buffer.isEmpty()) {
            // dequeue packet
            cPacket *pkt = (cPacket *)buffer.pop();
            bufferSizeVector.record(buffer.getLength());
            // send packet
            send(pkt, "toApp");
            // start new service
            serviceTime = pkt->getDuration();
            scheduleAt(simTime() + serviceTime, endServiceEvent);
        }
    } else if (msg->getKind() == 2){ // if msg is a feedback packet
        createFeedback();
    } else { // if msg is a data packet
        enqueuePacket(msg);
    }
}


void TransportRx::createFeedback() {
    // Feedback message initialization
    FeedbackPkt *feedbackPkt = new FeedbackPkt();
    // set packet type to Feedback (2)
    feedbackPkt->setKind(2);
    feedbackPkt->setByteLength(20);
    feedbackPkt->setBufferFeedbackFull(true);
    send(feedbackPkt, "toOut$o");
}


void TransportRx::enqueuePacket(cMessage *msg) {
    if (buffer.getLength() >= par("bufferSize").intValue()) {
        // drop the packet
        delete msg;
        this->bubble("packet dropped");
        packetDrop++;
        packetDropVector.record(packetDrop);
    } else {


        int limite = 0.8 * par("bufferSize").intValue();

        if (buffer.getLength() >= limite){
            createFeedback();
        }


         // enqueue the packet
        buffer.insert(msg);
        bufferSizeVector.record(buffer.getLength());
        // if the server is idle
        if (!endServiceEvent->isScheduled()) {
            // start the service
            scheduleAt(simTime() + 0, endServiceEvent);
        }
    }
}

#endif /* TransportRx */
