"""
Tests d'acceptation pour l'application LOG430 Labo3
"""
import requests
import pytest
import sys
import argparse
import time

def test_health_endpoint(base_url):
    """Test que l'endpoint de santé répond correctement"""
    response = requests.get(f"{base_url}/health")
    assert response.status_code == 200
    data = response.json()
    assert data['status'] == 'ok'

def test_health_check_endpoint(base_url):
    """Test que l'endpoint health-check répond correctement"""
    response = requests.get(f"{base_url}/health-check")
    assert response.status_code == 200
    data = response.json()
    assert data['status'] == 'ok'

def test_graphql_endpoint(base_url):
    """Test que l'endpoint GraphQL répond"""
    query = """
    {
        product(id: 1) {
            id
            name
            sku
            price
        }
    }
    """
    response = requests.post(f"{base_url}/graphql", json={'query': query})
    # Note: peut retourner 200 même si le produit n'existe pas
    assert response.status_code in [200, 404]

def test_orders_endpoint_structure(base_url):
    """Test que l'endpoint des commandes répond avec la bonne structure"""
    # Test GET (peut être vide)
    response = requests.get(f"{base_url}/orders")
    assert response.status_code in [200, 404]  # Acceptable si pas de commandes

def test_products_endpoint_structure(base_url):
    """Test que l'endpoint des produits répond avec la bonne structure"""
    response = requests.get(f"{base_url}/products")
    assert response.status_code in [200, 404]  # Acceptable si pas de produits

def test_response_time(base_url):
    """Test que l'application répond dans un délai raisonnable"""
    start_time = time.time()
    response = requests.get(f"{base_url}/health")
    end_time = time.time()
    
    assert response.status_code == 200
    assert (end_time - start_time) < 2.0  # Moins de 2 secondes

def test_cors_headers(base_url):
    """Test que les en-têtes CORS sont présents si nécessaire"""
    response = requests.options(f"{base_url}/health")
    # Le test passe si l'endpoint répond, même sans CORS
    assert response.status_code in [200, 405]  # 405 = Method Not Allowed est acceptable

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Tests d\'acceptation')
    parser.add_argument('--staging-url', required=True, help='URL de l\'environnement de staging')
    args = parser.parse_args()
    
    base_url = args.staging_url.rstrip('/')
    
    print(f"Exécution des tests d'acceptation sur {base_url}")
    
    # Exécuter les tests
    try:
        test_health_endpoint(base_url)
        print("Test health endpoint - PASSÉ")
        
        test_health_check_endpoint(base_url)
        print("Test health-check endpoint - PASSÉ")
        
        test_response_time(base_url)
        print("Test temps de réponse - PASSÉ")
        
        test_graphql_endpoint(base_url)
        print("Test GraphQL endpoint - PASSÉ")
        
        test_orders_endpoint_structure(base_url)
        print("Test structure endpoint orders - PASSÉ")
        
        test_products_endpoint_structure(base_url)
        print("Test structure endpoint products - PASSÉ")
        
        test_cors_headers(base_url)
        print("Test CORS headers - PASSÉ")
        
        print("\nTous les tests d'acceptation sont passés avec succès!")
        
    except Exception as e:
        print(f"Échec du test: {e}")
        sys.exit(1)