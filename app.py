#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import os
from flask import Flask, request, render_template, jsonify
from main import main as template_main

app = Flask(__name__)

@app.route("/", methods=['GET','POST'])
def index():
    if request.method == 'POST':
        user_input = request.form.get('user_input')
        
        if user_input:
            result = template_main(user_input)
            return jsonify(result=result)
        else:
            return jsonify(result='Input needed')        
        
    return render_template("index.html")

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)