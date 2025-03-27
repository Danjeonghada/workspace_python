from flask import Flask, request, render_template
import pickle

app = Flask(__name__)
with open("spam_model.pkl", "rb") as f:
    model = pickle.load(f)
with open("vectorizer.pkl", "rb") as f:
    vectorizer = pickle.load(f)

    @app.route("/", methods=['GET', 'POST'])
    def index():
        prediction = None
        if request.method == "POST":
            message = request.form['message']
            vec = vectorizer.transform([message]) # 적용할때는 fit_transform, 사용할 때는 transform
            result = model.predict(vec)[0]
            prediction = '🚨스팸 입니다!' if result == 1 else '✅정상 입니다.'
        return render_template("index.html", prediction=prediction)

if __name__ == '__main__':
    app.run(debug=True)