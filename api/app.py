# %%
import pickle
import pandas as pd
from flask import Flask, request, jsonify
from flask_cors import CORS

# %%
with open("../assets/models/decision-tree.pkl", "rb") as f:
    model = pickle.load(f)
arbre = model['model']

# %%
app = Flask(__name__)
app.config['SECRET_KEY'] = 'a-secret-key'

cors = CORS(app, resources={r'/*': {'origin': '*'}})

# %%
@app.route('/estimate', methods=['GET'])
def estimate():
    nbLots = request.args.get('nb-lot')
    nbPieces = request.args.get('nb-piece')
    X = pd.DataFrame([[nbLots, nbPieces]], columns=arbre.feature_names_in_)
    typeLocal = arbre.predict(X)[0]
    result = {'data': typeLocal}
    return jsonify(result)

# %%
if __name__ == '__main__':
    app.run()


