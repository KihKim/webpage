#!/usr/bin/env python
from flask import Flask, render_template, Response, redirect
from flask import Flask, flash, redirect, render_template, request, session, abort
from camera import Camera
import sys
import paho.mqtt.client as mqtt
import threading
import time
import os
num = 0
def on_connect(client, userdata, flags,rc):
    print('Connected with result {0}'.format(rc))
    client.subscribe('temp')
     
def on_message(client, userdata, msg):
    global num
    m = msg.payload.decode("utf-8")
    if msg.topic == 'temp':
        num = int(m)
    print(m)
    
client = mqtt.Client()
client.connect('localhost',1883,60)
client.on_connect = on_connect
client.on_message = on_message



app = Flask(__name__)

@app.route('/')
def index():
    global num, client
    
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return render_template('index.html', num=num)
def gen(camera):
   while 1:
       frame = camera.get_frame()
       yield (b'--frame\r\n'
              b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
       
@app.route('/login', methods=['POST'])
def do_admin_login():
    if request.form['password'] == 'codu1234' and request.form['username'] == 'CODU':
        session['logged_in'] = True
    else:
        flash('wrong password!')
    return index()





@app.route('/Open/')
def button_clicked():
    global client
    client = mqtt.Client()
    client.connect('localhost',1883,60)
    client.publish('W','Open')
    return redirect('/')
   
@app.route('/Close/')
def button_clicked2():
    global client
    client = mqtt.Client()
    client.connect('localhost',1883,60)
    client.publish('W','Close')
    return redirect('/')

@app.route('/logout/')
def button_clicked3():
    session['logged_in'] = False
    return redirect('/')

@app.route('/video')
def video():
   return Response(gen(Camera()),
                   mimetype='multipart/x-mixed-replace; boundary=frame')
def test():
   global client
   client.loop_start()
   
if __name__ == '__main__':
   threading.Timer(1,test).start()
   app.secret_key = os.urandom(12)
   app.run(host='192.168.0.17', debug=True,threaded = True , port = 8000) #Host is your Localhost address
