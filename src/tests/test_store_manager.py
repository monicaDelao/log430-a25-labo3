"""
Tests for orders manager
SPDX - License - Identifier: LGPL - 3.0 - or -later
Auteurs : Gabriel C. Ullmann, Fabio Petrillo, 2025
"""

import json
import time

import sys
import os
import pytest

# Ajouter le répertoire parent au path pour permettre l'import
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from store_manager import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_health(client):
    result = client.get("/health-check")
    assert result.status_code == 200
    assert result.get_json() == {"status": "ok"}


def test_stock_flow(client):
    # Créer des données uniques pour éviter les conflits de clés
    timestamp = str(int(time.time()))

    # D'abord, créer un utilisateur nécessaire pour les commandes
    user_data = {
        "name": f"Test User {timestamp}",
        "email": f"test{timestamp}@example.com",
    }
    user_response = client.post(
        "/users", data=json.dumps(user_data), content_type="application/json"
    )
    assert user_response.status_code == 201  # POST - 201 Created
    user_data = user_response.get_json()
    user_id = user_data["user_id"]
    assert user_id > 0

    # 1. Créez un article (POST /products)
    product_data = {
        "name": f"Test Product {timestamp}",
        "sku": f"TEST{timestamp}",
        "price": 15.99,
    }
    product_response = client.post(
        "/products", data=json.dumps(product_data), content_type="application/json"
    )

    assert product_response.status_code == 201  # POST - 201 Created
    product_data = product_response.get_json()
    product_id = product_data["product_id"]  # L'API retourne 'product_id'
    assert product_id > 0

    # 2. Ajoutez 5 unités au stock de cet article (POST /stocks)
    stock_data = {"product_id": product_id, "quantity": 5}
    stock_response = client.post(
        "/stocks", data=json.dumps(stock_data), content_type="application/json"
    )
    assert stock_response.status_code == 201  # POST - 201 Created

    # 3. Vérifiez le stock, votre article devra avoir 5 unités dans le stock (GET /stocks/:id)
    stock_check_response = client.get(f"/stocks/{product_id}")
    assert (
        stock_check_response.status_code == 201
    )  # Note: L'API retourne 201 (devrait être 200)
    stock_check_data = stock_check_response.get_json()
    assert stock_check_data["quantity"] == 5

    # 4. Faites une commande de 2 unités de l'article que vous avez créé (POST /orders)
    order_data = {
        "user_id": user_id,
        "items": [{"product_id": product_id, "quantity": 2}],
    }
    order_response = client.post(
        "/orders", data=json.dumps(order_data), content_type="application/json"
    )
    assert order_response.status_code == 201  # POST - 201 Created
    order_data = order_response.get_json()
    order_id = order_data["order_id"]  # L'API retourne 'order_id'
    assert order_id > 0

    # 5. Vérifiez le stock encore une fois (GET /stocks/:id)
    # Le stock devrait être réduit à 3 unités (5 - 2 = 3)
    stock_after_order_response = client.get(f"/stocks/{product_id}")
    assert (
        stock_after_order_response.status_code == 201
    )  # Note: L'API retourne 201 (devrait être 200)
    stock_after_order_data = stock_after_order_response.get_json()
    assert stock_after_order_data["quantity"] == 3

    # 6. Étape extra: supprimez la commande et vérifiez le stock de nouveau
    # Le stock devrait augmenter après la suppression de la commande
    delete_order_response = client.delete(f"/orders/{order_id}")
    assert delete_order_response.status_code == 200  # DELETE - 200 OK
    delete_data = delete_order_response.get_json()
    assert delete_data["deleted"] is True  # L'API retourne {"deleted": True}

    # Vérifier que le stock est restauré à 5 unités
    stock_after_delete_response = client.get(f"/stocks/{product_id}")
    assert (
        stock_after_delete_response.status_code == 201
    )  # Note: L'API retourne 201 (devrait être 200)
    stock_after_delete_data = stock_after_delete_response.get_json()
    assert stock_after_delete_data["quantity"] == 5
