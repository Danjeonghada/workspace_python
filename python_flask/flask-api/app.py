from flask import Flask, jsonify, request, abort
from scripts.regsetup import description

app = Flask(__name__)

# 샘플 데이터 저장용
items = {
    1: {"name": "apple", "price": 1000},
    2: {"name": "banana", "price": 500}
}

# GET: 전체 목록 조회
@app.route("/items", methods=["GET"])
def get_items():
    return jsonify(items)

# GET: 특정 아이템 조회
@app.route("/items/<int:item_id>", methods=["GET"])
def get_item(item_id):
    item = items.get(item_id)
    if item:
        return jsonify(item)
    else:
        abort(404, description="Item not found")

# POST: 아이템 추가
@app.route("/items", methods=["POST"])
def create_item():
    data = request.get_json()
    if not data or 'name' not in data or 'price' not in data:
        abort(400, description='Invalid data')
    new_id = max(items.keys(), default=0) + 1
    items[new_id] = {'name': data['name'], 'price': data['price']}
    # 200 요청 성공, 201(생성됨), 202(승인됨)
    return jsonify({new_id: items[new_id]}), 201

# PUT: 아이템 수정
@app.route('/items/<int:item_id>', methods=['PUT'])
def update_item(item_id):
    if item_id not in items:
        abort(404, description='Item not found')
    data = request.get_json()
    if not data:
        abort(400, description='Invalid data')
    items[item_id].update(data)
    return jsonify({item_id: items[item_id]})
# DELETE : 아이템 삭제
@app.route("/items/<int:item_id>", methods=['DELETE'])
def delete_item(item_id):
    if item_id not in items:
        abort(404, description='Item not found')
    delete = items.pop(item_id)
    return jsonify({'delete' : delete})


if __name__ == '__main__':
    app.run(debug=True)
