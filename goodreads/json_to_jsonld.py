import json

with open('goodreads.json', 'r') as json_file, open(
        'goodreads_ld_new.jsonld', 'w') as json_ld_file:
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
            isbn = json_line['isbn'][0]
            try:
                genres = json_line['genres']
            except KeyError:
                genres = []
            try:
                pages = json_line['pages'][0]
            except KeyError:
                pages = ""

            try:
                rating = json_line["avg_rating"][0]
            except (KeyError, IndexError):
                rating = []

            try:
                no_reviews = json_line["number_of_reviews"][0]
            except (KeyError, IndexError):
                no_reviews = ""

            try:
                languages = json_line["languages"]
            except KeyError:
                languages = []

            try:
                format = json_line["book_format"][0]
            except (KeyError, IndexError):
                format = ""

            try:
                authors = json_line["authors"]
            except KeyError:
                authors = []

            new_json = {
                "@context": "https://schema.org/docs/jsonldcontext.jsonld",
                "@type": "Book",
                "@id": isbn,
                "name": json_line['book_title'][0],
                "genre": genres,
                "author": {
                    "@type": "Person",
                    "@id": "".join([
                        author.replace('.', '').replace(' ', '').replace(
                            ':', '').replace(',',  '').replace(';', '')
                        for author in authors if author]),
                    "name": "; ".join([author for author in authors]) if
                    authors else authors
                  },
                "numberOfPages": pages,
                "aggregateRating": {
                    "@type": "AggregateRating",
                    "@id": f"{isbn}-rating",
                    "ratingValue": rating,
                    "reviewCount": no_reviews
                  },
                "inLanguage": "; ".join([lang for lang in languages]),
                "bookFormat": format,
                "review": []
            }

            reviews = json_line["reviews"][0]
            for review in reviews:
                user_name = reviews[review]['user_name']
                user_id = review.replace(':', '')
                user_review = reviews[review]['user_review'][:100]
                user_rating = reviews[review]['user_rating']
                user_likes_count = reviews[review]['user_review_likes']

                review_dict = {
                    "@type": "Review",
                    "@id": f"{isbn}-{user_id}",
                    "reviewer": {
                        "@type": "Person",
                        "@id": user_id,
                        "name": user_name
                    },
                    "reviewBody": user_review,
                    "reviewRating": user_rating,
                    "interactionStatistic": user_likes_count
                }
                new_json["review"].append(review_dict)
            json_ld_file.write(json.dumps(new_json))
            json_ld_file.write("\n")
