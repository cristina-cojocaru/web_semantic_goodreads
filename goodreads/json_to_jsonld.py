import json

with open('goodreads.json', 'r') as json_file, open(
        'goodreads_ld_smaller.json', 'w') as json_ld_file:
    for line in json_file:
        line = line.strip()
        if not line.startswith('[') and not line.startswith(']'):
            if line[len(line)-1] == ',' or line[len(line)-1] == '[':
                line = line[:-1]
            try:
                json_line = json.loads(line)
            except json.decoder.JSONDecodeError as e:
                print('=====ERROR=====')
                print(e)
                print(line)
                print('====end of error===')
                break
            try:
                genres = json_line['genres']
            except KeyError:
                genres = []
            try:
                pages = json_line['pages']
            except KeyError:
                pages = []

            try:
                rating = json_line["avg_rating"]
            except KeyError:
                rating = []

            try:
                no_reviews = json_line["number_of_reviews"]
            except KeyError:
                no_reviews = []

            try:
                languages = json_line["languages"]
            except KeyError:
                languages = []

            try:
                format = json_line["book_format"]
            except KeyError:
                format = []

            try:
                authors = json_line["authors"]
            except KeyError:
                authors = []

            new_json = {
                "@context": {
                    "book_title": "http://schema.org/name",
                    "genres": "http://schema.org/genre",
                    "isbn": "http://schema.org/identifier",
                    "authors": "http://schema.org/author",
                    "pages": "http://schema.org/numberOfPages",
                    "avg_rating": "http://schema.org/ratingValue",
                    "number_of_reviews": "http://schema.org/reviewCount",
                    "languages": "http://schema.org/inLanguage",
                    "book_format": "http://schema.org/bookFormat",
                    "reviewers": {
                        "@id": "http://schema.org/review",
                        "@container": "@set",
                        "@type": "@id"
                    },
                    "user_name": "http://schema.org/name",
                    "user_review": "http://schema.org/reviewBody",
                    "user_rating": "http://schema.org/ratingValue",
                    "user_review_likes": "http://schema.org/interactionCount"
                },
                "http://schema.org/name": json_line["book_title"],
                "http://schema.org/genre": genres,
                "http://schema.org/identifier": json_line["isbn"],
                "http://schema.org/author": authors,
                "http://schema.org/numberOfPages": pages,
                "http://schema.org/ratingValue": rating,
                "http://schema.org/reviewCount": no_reviews,
                "http://schema.org/inLanguage": languages,
                "http://schema.org/bookFormat": format,
                "http://schema.org/review": []
            }
            reviews = json_line["reviews"][0]
            for review in reviews:
                review_dict = {"@id": review,
                     "http://schema.org/name": reviews[review]['user_name'],
                     "http://schema.org/reviewBody": reviews[review][
                         'user_review'][:100],
                     "http://schema.org/ratingValue": reviews[review][
                         'user_rating'],
                     "http://schema.org/interactionCount": reviews[review][
                         'user_review_likes']
                     }
                new_json["http://schema.org/review"].append(review_dict)
            json_ld_file.write(json.dumps(new_json))
            json_ld_file.write("\n")
