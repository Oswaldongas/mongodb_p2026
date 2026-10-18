#!/usr/bin/env python3
import argparse
import logging
import os
import requests


# Set logger
log = logging.getLogger()
log.setLevel('INFO')
handler = logging.FileHandler('books.log')
handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
log.addHandler(handler)

# Read env vars related to API connection
BOOKS_API_URL = os.getenv("BOOKS_API_URL", "http://localhost:8000")



def print_book(book):
    for k in book.keys():
        print(f"{k}: {book[k]}")
    print("="*50)

#Enlista los libros que cumplan con los parametros de busqueda, si no se pasan parametros, lista todos los libros
def list_books(rating, pages, title, limit, skip):
    suffix = "/books"
    endpoint = BOOKS_API_URL + suffix

    #Ahora lo construyo dinamicamente con los parámetros que me pasen
    params = {}
    if rating:
        params["rating"] = rating
    if pages:
        params["pages"] = pages
    if title:
        params["title"] = title
    if limit:
        params["limit"] = limit
    if skip:
        params["skip"] = skip

    #Convierte el diccionario en parametros de una url
    response = requests.get(endpoint, params=params)
    if response.ok:
        json_resp = response.json()
        for book in json_resp:
            print_book(book)
    else:
        print(f"Error: {response}")


def get_book_by_id(id):
    suffix = f"/books/{id}"
    endpoint = BOOKS_API_URL + suffix
    response = requests.get(endpoint)
    if response.ok:
        json_resp = response.json()
        print_book(json_resp)
    else:
        print(f"Error: {response}")


def update_book(id):
    suffix = f"/books/{id}"
    endpoint = BOOKS_API_URL + suffix
    response = requests.get(endpoint)
    if not response.ok:
        print(f"Error: {response}")
        return

    book = response.json()
    book.pop("_id", None)
    print("Press Enter to keep the current value")
    for k in book.keys():
        value = input(f"{k} [{book[k]}]: ").strip()
        if value:
            if isinstance(book[k], list):
                book[k] = [v.strip() for v in value.split(",")]
            else:
                book[k] = value

    response = requests.put(endpoint, json=book)
    if response.ok:
        json_resp = response.json()
        print_book(json_resp)
    else:
        print(f"Error: {response}")


def delete_book(id):
    suffix = f"/books/{id}"
    endpoint = BOOKS_API_URL + suffix
    response = requests.delete(endpoint)
    if response.ok:
        print(f"Book {id} deleted")
    else:
        print(f"Error: {response}")

#Nueva funcion para el agreggation
def get_analytics():
    endpoint = BOOKS_API_URL + "/books/analytics"
    response = requests.get(endpoint)
    if response.ok:
        json_resp = response.json()
        print("=== TOP 10 AUTORES DE JOYAS POCO CONOCIDAS ===")
        for index, author in enumerate(json_resp, 1):
            print(f"{index}. {author['_id']}")
            print(f"   Libros 'Joya Poco Conocida': {author['hidden_gems_count']}")
            print(f"   Calificación Promedio: {author['avg_rating']:.2f}")
            print("-" * 40)
    else:
        print(f"Error: {response}")


def main():
    log.info(f"Welcome to books catalog. App requests to: {BOOKS_API_URL}")

    parser = argparse.ArgumentParser()

    list_of_actions = ["search", "get", "update", "delete", "analytics"]

    #Lista de argumentos que puede recibir la terminal para interactuar con la API de libros
    parser.add_argument("action", choices=list_of_actions,
            help="Action to be user for the books library")
    parser.add_argument("-i", "--id",
            help="Provide a book ID which related to the book action", default=None)
    parser.add_argument("-r", "--rating",
            help="Search parameter to look for books with average rating equal or above the param (0 to 5)", default=None)
    parser.add_argument("--pages",
            help="Search parameter for number of pages (equal or above)", default=None)
    parser.add_argument("-t", "--title", 
            help="Search parameter for book title (partial match)", default=None)
    parser.add_argument("--limit", 
            help="Limit the number of results", type=int, default=None)
    parser.add_argument("--skip", 
            help="Number of results to skip", type=int, default=None)

    args = parser.parse_args()

    if args.id and not args.action in ["get", "update", "delete"]:
        log.error(f"Can't use arg id with action {args.action}")
        exit(1)

    if args.rating and args.action != "search":
        log.error(f"Rating arg can only be used with search action")
        exit(1)

    #Cambios para los nuevos parametros de busqueda
    if args.action == "search":
        list_books(args.rating, args.pages, args.title, args.limit, args.skip)

    elif args.action == "get" and args.id:
        get_book_by_id(args.id)

    elif args.action == "update":
        update_book(args.id)

    elif args.action == "delete":
        delete_book(args.id)

    #Para el analytics
    elif args.action == "analytics":
        get_analytics()    

if __name__ == "__main__":
    main()