from flask import Flask, render_template, request, flash, redirect, url_for
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

@app.route('/')
def inicio():
    return render_template('inicio.html')

@app.route('/saiba-mais')
def saiba_mais():
    return render_template('saiba_mais.html')

@app.route('/contato', methods=['GET', 'POST'])
def contato():
    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        mensagem = request.form.get('mensagem')
        
        if nome and email and mensagem:
            flash('Mensagem enviada com sucesso! Entraremos em contato em breve.', 'success')
            return redirect(url_for('contato'))
        else:
            flash('Por favor, preencha todos os campos.', 'error')
    
    return render_template('contato.html')

@app.route('/sobre-nos')
def sobre_nos():
    return render_template('sobre_nos.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)