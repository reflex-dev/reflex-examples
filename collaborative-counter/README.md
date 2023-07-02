
# Collaborative Counter

- **This collaborative counter demonstrates a very simple collaborative web app.**   
The well-known example of collaborative web app are Google Docs. Collaborative software or groupware is application software designed to help people working on a common task to attain their goals. 
- **All clients can see the latest value on the counter fast**,   
Anyone of them can change the counter value by clicking the button or sending an HTTP request. After changing the new value, All clients can see the new value on the counter quickly.
- **And it can also support IoT applications**   
It can support IoT application if you would like to integrate with them. For example, Raspberry Pi PICO sends the counter value through MQTT. And some MQTT python processes can subscribe correct topic to receive this message, and then send an HTTP request to this collaborative counter web app.   

## Current approach
- Tick: Use the Tick pattern to update UI whenever the state is changing
- State Manager: Use state manager to update every state for every client
- API Routes: use API Routes to allow changing state from another place.

## The way to integrate IoT device
- write a simple .py that subscribe your specific topic on mqtt server and then send request to api route.
- When api route receive changed count value, publish to specific topic on mqtt server. 
- Make a simple IoT counter device that support MQTT publish/subscribe.  You can make Raspberry PICO + micropython to do that if you only know how to write python.

## Demo 
Demo Video  
https://github.com/pynecone-io/pynecone-examples/assets/12568287/135ecee5-b9d6-42a9-99d3-e0f52980aeb5
