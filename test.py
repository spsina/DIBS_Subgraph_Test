import requests

wBNB = "0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c" # address of wBNB on bsc
SUBGRAPH_ENDPOINT = "https://api.thegraph.com/subgraphs/name/spsina/dibsdata"

def query(query_str):
    request = requests.post(SUBGRAPH_ENDPOINT, json={'query': query_str})
    if request.status_code != 200:
        raise Exception("Could Not Fetch Results")
    
    return request.json().get('data')

def get_all_pairs_and_tokens():
    print("[INFO] Fetching pairs and tokens")
    tokens = set()
    pairs = {} # {pairAddress: [token0, token1]}
    query_str = """
    {
        pairs(first: 1000) {
            id
            token0
            token1
        }
    }    
    """
    pairs_array = query(query_str).get('pairs')

    for pair in pairs_array:
        pairs[pair.get('id')] = [pair.get('token0'), pair.get('token1')]
        tokens.add(pair.get('token0'))
        tokens.add(pair.get('token1'))
    
    return pairs, tokens
    


def get_all_paths():
    print("[INFO] Fetching paths")
    paths = {} # {tokenAddress: [list of pairAddress]}
    query_str = """
    {
        pathToTargets (first: 1000, where: {target: "%s"}) {
            token
            path
        }
    }
    """ % (wBNB)

    paths_array = query(query_str).get('pathToTargets')

    for path in paths_array:
        paths[path.get('token')] = path.get('path')
    
    return paths


def assert_path_correctness(pairs, paths):
    print("[INFO] Asserting all paths lead to wBNB")
    
    for token, path in paths.items():
        start_token = token
        if start_token == wBNB:
            continue
        
        for i, pair_address in enumerate(path):
            pair_tokens = pairs.get(pair_address)

            # make sure start token is in pair_tokens 
            try:
                assert start_token in pair_tokens
            except AssertionError:
                print("\t[**PAIR_ERROR]", token)
           

            other_token = pair_tokens[0] if start_token == pair_tokens[1] else pair_tokens[1]
            
            # or other_token must be wBNB address
            if i == len(path) - 1:
                try:
                    assert other_token == wBNB
                except AssertionError:
                    print("\t[**PATH_ERROR]", token, [start_token, other_token])
            else:
                start_token = other_token

def assert_all_tokens_have_path_to_wBNB(tokens, paths):
    print("[INFO] Asserting all tokens have a path to wBNB")

    tokens_with_path = set(paths.keys())
    tokens_with_no_path = tokens.difference(tokens_with_path)

    try:
        assert len(tokens_with_no_path) == 0
    except AssertionError:
        for token_with_no_path in tokens_with_no_path:
            print("\t[**NO_PATH] ", token_with_no_path)

if __name__ == "__main__":
    pairs, tokens = get_all_pairs_and_tokens()
    paths = get_all_paths()
    
    assert_path_correctness(pairs, paths)
    assert_all_tokens_have_path_to_wBNB(tokens, paths)
