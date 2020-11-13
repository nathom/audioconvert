from tagger import *
import discogs
import spotify

if __name__ == "__main__":
    path = argv[1]
    try:
        no_disc = (argv[2] == '-n')
    except:
        no_disc = False

    getFilename = lambda path: path.split('/')[-1]

    filename = getFilename(path)
    query = ' '.join(findall('\w+', filename))
    history = query
    tags = discogs.search_album(query)
    if tags != 0:
        try_match(tags, path)
    else:
        print('Matches could not automatically be found.')
        pass
    item = 0
    unsatisfied = True
    while unsatisfied:
        query = input('Press enter to continue. Type \'n\' to get next result. Type anything else to manual search.\n')
        if query == 'n':
            item += 1
            tags = discogs.search_album(history, result_item=item)
            if tags != 0:
                try_match(tags, path)
            else:
                print('Matches could not automatically be found.')
                pass
        elif query != '':
            tags = discogs.search_album(query)

            if tags != 0:
                try_match(tags, path)
            else:
                print('Matches could not automatically be found.')
                pass
        else:
            matched_tags, not_matched = match_tags(tags, path)
            unsatisfied = False

    input('Press enter to confirm tags.')
    set_tags(matched_tags, no_disc)
    print('Finished.')




