from time import time
import matplotlib.pyplot as plt
from collections import deque

class Timer():
    def __init__(self):
        self.initial_time = None
        self.tic = None
        self.times_list = []

    def start(self):
        if self.initial_time is None:
            self.initial_time = time()
        self.tic = time()

    def stop(self, accumulate=False):
        dt = time() - self.tic
        if accumulate:
            self.times_list.append(dt)
        print("dt = {:.4e} sec".format(dt))

    def cumulative(self):
        dt = sum(self.times_list)
        print("Cumulative time = {:.4e} sec".format(dt))

class Solution:
    def __init__(self):
        self.word_to_idx = None
        self.idx_to_word = None
        self.adjacency_dict = None

    def isAdjacent(self, w1, w2):
        """ Figures out if words are 'adjacent' to each other. """
        differences = 0
        for c1, c2 in zip(w1, w2):
            if c1 != c2:
                differences += 1
                if differences > 1:
                    return False
        if differences == 1:
            return True
        else:
            return False

    def makeAdjacencyDict(self, words):
        """ Makes an adjacency dictionary from the word list in the form of a dictionary mapping nodes to
        their adjacent nodes. This implementation is O(|s|*|V|^2), which is super inefficient if there are
        a lot of vertices in the graph. """
        # First, map words to their index in the list (and vice versa), since manipulating integers is
        # easier than strings
        self.word_to_idx = {w: i for i, w in enumerate(words)}
        self.idx_to_word = {i: w for i, w in enumerate(words)}
        # Initialize empty dict
        adjacency_dict = {i: [] for i in range(len(words))}
        for i1, w1 in enumerate(words[:-1]):
            for i2, w2 in enumerate(words[i1 + 1:], start=i1 + 1):
                if self.isAdjacent(w1, w2):
                    adjacency_dict[i1].append(i2)
                    adjacency_dict[i2].append(i1)
        self.adjacency_dict = adjacency_dict

    def makeAdjacencyDict_(self, words):
        """
        Makes an adjacency dictionary by iteratively deleting characters from each word in the
        word list, then running through the remaining strings and grouping them if they are identical
        using a dictionary. This way is O(|s|*|V|) in the best case, O(|s|*|V|^2) in the worst case,
        depending on the degree of connectivity of the graph.
        """
        # First, map words to their index in the list (and vice versa), since manipulating integers
        # is easier than strings
        timer = Timer()
        self.word_to_idx = {w: i for i, w in enumerate(words)}
        self.idx_to_word = {i: w for i, w in enumerate(words)}
        # Initialize empty dict and similar word groups
        adjacency_dict = {i: [] for i in range(len(words))}
        #adjacency_dict_ = {}
        # Loop over characters in the string to delete
        for i in range(len(words[0])):
            # Put similar words in groups
            word_groups = {}
            for j in range(len(words)):
                # Delete character in the i^th position from the string
                modified_word = words[j][:i] + words[j][(i+1):]
                if modified_word in word_groups:
                    word_groups[modified_word].append(j)
                else:
                    word_groups[modified_word] = [j]


            # Put all similar words in adjacency lists
            # Iterate over all word groups, then unique pairs of word indices in each group
            #timer.start()
            for group in word_groups:
                for j, idx1 in enumerate(word_groups[group]):
                    for idx2 in word_groups[group][j+1:]:
                        # Add pair to each other's adjacency dictionary
                        adjacency_dict[idx1].append(idx2)
                        adjacency_dict[idx2].append(idx1)
                    #adjacency_dict_[idx1] = word_groups[group] #word_groups[group][:j] + word_groups[group][j+1:]
            #timer.stop(accumulate=True)
        self.adjacency_dict = adjacency_dict
        #timer.cumulative()

    def findLadders(self, beginWord, endWord, wordList):
        """
        Finds shortest paths in a two-step process:
            1) Uses BFS to find the shortest distance between beginWord and every other word
                a) If we find endWord before reaching the last level, just stop there; we only need to consider nodes to
                a depth just above endWord
                b) Label each word with its distance from beginWord
            2) Find all paths from beginWord to endWord through pruned graph
                a) Only consider edges where graph depth increases monotonically
        :type beginWord: str
        :type endWord: str
        :type wordList: List[str]
        :rtype: List[List[str]]
        """
        # Immediately detect edge cases
        if (endWord not in wordList):
            return []
        elif (beginWord == endWord) or (self.isAdjacent(beginWord, endWord)):
            return [[beginWord, endWord]]

        # Make adjacency dict from word list
        if beginWord not in wordList:
            wordList.append(beginWord)
        self.makeAdjacencyDict_(wordList)

        # Convert words to indices
        start = self.word_to_idx[beginWord]
        end = self.word_to_idx[endWord]

        # Function for performing BFS, returning a dictionary mapping depth (from start) to nodes
        def BFS(start, end):
            visited_nodes = [False] * len(wordList)
            visited_nodes[start] = True
            pruned_nodes = {}
            nodes_to_visit = deque([start])
            depth = -1
            done = False
            while not done:
                depth += 1
                pruned_nodes[depth] = []
                # Iterate over all nodes present in deque
                for n in range(len(nodes_to_visit)):
                    # Pop node from right end of deque
                    node = nodes_to_visit.pop()
                    # Check if popped node is end, add it to pruned graph and break loop
                    if node == end:
                        pruned_nodes[depth] = [node]
                        done = True
                        break
                    # Look up all its adjacent nodes and add them to the left end of the deque if they
                    # haven't already been visited
                    adjacent_nodes = self.adjacency_dict[node]
                    for adj_node in adjacent_nodes:
                        if not visited_nodes[adj_node]:
                            nodes_to_visit.appendleft(adj_node)
                            visited_nodes[adj_node] = True
                    # Also add node to the pruned graph and mark as visited
                    pruned_nodes[depth].append(node)
                    visited_nodes[node] = True
                # If deque is empty but not all nodes have been visited, there is no way to reach end from start
                if (not done) and (len(nodes_to_visit) == 0) and (not all(visited_nodes)):
                    return []
            return pruned_nodes

        # Perform BFS from start to end and end to start
        depth_from_start = BFS(start, end)
        depth_from_end = BFS(end, start)
        # Min path length is length of dictionaries
        min_path_length = len(depth_from_start)-1
        assert min_path_length == len(depth_from_end)-1

        # Invert dictionaries to map idx to depth
        def invert_dict(d):
            d_ = {}
            for key in range(len(d)):
                for value in d[key]:
                    d_[value] = key
            return d_

        depth_from_start = invert_dict(depth_from_start)
        depth_from_end = invert_dict(depth_from_end)

        # Now, knowing the pruned graph and depth to each node, we enumerate all paths from start to end along nodes
        # which have depths (from start and end) which sum to the length of the minimum path
        possible_paths = deque([[start]])
        visited_nodes = []
        # Enter loop
        done = False
        while not done:
            # Iterate over possible_paths
            for p in range(len(possible_paths)):
                path = possible_paths.popleft()
                if path[-1] == end:
                    done = True
                    break
                # Enumerate all nodes adjacent to end of path
                adj_nodes = self.adjacency_dict[path[-1]]
                # Filter adjacent nodes to ensure their depth is monotonically increasing (preventing backtracking)
                adj_nodes = list(filter(lambda node: depth_from_start.get(node) == depth_from_start.get(path[-1], 2*min_path_length)+1, adj_nodes))
                adj_nodes = list(filter(lambda node: depth_from_end.get(node) == depth_from_end.get(path[-1], 2*min_path_length)-1, adj_nodes))
                # Create new paths to adjacent nodes and append to possible paths
                for node in adj_nodes:
                    possible_paths.append(path + [node])
            if (len(adj_nodes) == 0) or all([len(path)-1 == min_path_length for path in possible_paths]):
                break

        # Convert back from index to words
        possible_paths = [[self.idx_to_word[idx] for idx in path] for path in possible_paths]
        return possible_paths





# Test things
beginWords = ["hit", "hit", "a", "qa", "hot", "hot", "sand"]
endWords = ["cog", "cog", "c", "sq", "dog", "dog", "acne"]
wordLists = [
    ["hot", "dot", "dog", "lot", "log", "cog"],
    ["hot", "dot", "dog", "lot", "log"],
    ["a", "b", "c"],
    ["si","go","se","cm","so","ph","mt","db","mb","sb","kr","ln","tm","le","av","sm","ar","ci","ca","br","ti","ba","to","ra","fa","yo","ow","sn","ya","cr","po","fe","ho","ma","re","or","rn","au","ur","rh","sr","tc","lt","lo","as","fr","nb","yb","if","pb","ge","th","pm","rb","sh","co","ga","li","ha","hz","no","bi","di","hi","qa","pi","os","uh","wm","an","me","mo","na","la","st","er","sc","ne","mn","mi","am","ex","pt","io","be","fm","ta","tb","ni","mr","pa","he","lr","sq","ye"],
    ["hot","dog","cog","pot","dot"],
    ["hot", "dog"],
    ["slit","bunk","wars","ping","viva","wynn","wows","irks","gang","pool","mock","fort","heel","send","ship","cols","alec","foal","nabs","gaze","giza","mays","dogs","karo","cums","jedi","webb","lend","mire","jose","catt","grow","toss","magi","leis","bead","kara","hoof","than","ires","baas","vein","kari","riga","oars","gags","thug","yawn","wive","view","germ","flab","july","tuck","rory","bean","feed","rhee","jeez","gobs","lath","desk","yoko","cute","zeus","thus","dims","link","dirt","mara","disc","limy","lewd","maud","duly","elsa","hart","rays","rues","camp","lack","okra","tome","math","plug","monk","orly","friz","hogs","yoda","poop","tick","plod","cloy","pees","imps","lead","pope","mall","frey","been","plea","poll","male","teak","soho","glob","bell","mary","hail","scan","yips","like","mull","kory","odor","byte","kaye","word","honk","asks","slid","hopi","toke","gore","flew","tins","mown","oise","hall","vega","sing","fool","boat","bobs","lain","soft","hard","rots","sees","apex","chan","told","woos","unit","scow","gilt","beef","jars","tyre","imus","neon","soap","dabs","rein","ovid","hose","husk","loll","asia","cope","tail","hazy","clad","lash","sags","moll","eddy","fuel","lift","flog","land","sigh","saks","sail","hook","visa","tier","maws","roeg","gila","eyes","noah","hypo","tore","eggs","rove","chap","room","wait","lurk","race","host","dada","lola","gabs","sobs","joel","keck","axed","mead","gust","laid","ends","oort","nose","peer","kept","abet","iran","mick","dead","hags","tens","gown","sick","odis","miro","bill","fawn","sumo","kilt","huge","ores","oran","flag","tost","seth","sift","poet","reds","pips","cape","togo","wale","limn","toll","ploy","inns","snag","hoes","jerk","flux","fido","zane","arab","gamy","raze","lank","hurt","rail","hind","hoot","dogy","away","pest","hoed","pose","lose","pole","alva","dino","kind","clan","dips","soup","veto","edna","damp","gush","amen","wits","pubs","fuzz","cash","pine","trod","gunk","nude","lost","rite","cory","walt","mica","cart","avow","wind","book","leon","life","bang","draw","leek","skis","dram","ripe","mine","urea","tiff","over","gale","weir","defy","norm","tull","whiz","gill","ward","crag","when","mill","firs","sans","flue","reid","ekes","jain","mutt","hems","laps","piss","pall","rowe","prey","cull","knew","size","wets","hurl","wont","suva","girt","prys","prow","warn","naps","gong","thru","livy","boar","sade","amok","vice","slat","emir","jade","karl","loyd","cerf","bess","loss","rums","lats","bode","subs","muss","maim","kits","thin","york","punt","gays","alpo","aids","drag","eras","mats","pyre","clot","step","oath","lout","wary","carp","hums","tang","pout","whip","fled","omar","such","kano","jake","stan","loop","fuss","mini","byrd","exit","fizz","lire","emil","prop","noes","awed","gift","soli","sale","gage","orin","slur","limp","saar","arks","mast","gnat","port","into","geed","pave","awls","cent","cunt","full","dint","hank","mate","coin","tars","scud","veer","coax","bops","uris","loom","shod","crib","lids","drys","fish","edit","dick","erna","else","hahs","alga","moho","wire","fora","tums","ruth","bets","duns","mold","mush","swop","ruby","bolt","nave","kite","ahem","brad","tern","nips","whew","bait","ooze","gino","yuck","drum","shoe","lobe","dusk","cult","paws","anew","dado","nook","half","lams","rich","cato","java","kemp","vain","fees","sham","auks","gish","fire","elam","salt","sour","loth","whit","yogi","shes","scam","yous","lucy","inez","geld","whig","thee","kelp","loaf","harm","tomb","ever","airs","page","laud","stun","paid","goop","cobs","judy","grab","doha","crew","item","fogs","tong","blip","vest","bran","wend","bawl","feel","jets","mixt","tell","dire","devi","milo","deng","yews","weak","mark","doug","fare","rigs","poke","hies","sian","suez","quip","kens","lass","zips","elva","brat","cosy","teri","hull","spun","russ","pupa","weed","pulp","main","grim","hone","cord","barf","olav","gaps","rote","wilt","lars","roll","balm","jana","give","eire","faun","suck","kegs","nita","weer","tush","spry","loge","nays","heir","dope","roar","peep","nags","ates","bane","seas","sign","fred","they","lien","kiev","fops","said","lawn","lind","miff","mass","trig","sins","furl","ruin","sent","cray","maya","clog","puns","silk","axis","grog","jots","dyer","mope","rand","vend","keen","chou","dose","rain","eats","sped","maui","evan","time","todd","skit","lief","sops","outs","moot","faze","biro","gook","fill","oval","skew","veil","born","slob","hyde","twin","eloy","beat","ergs","sure","kobe","eggo","hens","jive","flax","mons","dunk","yest","begs","dial","lodz","burp","pile","much","dock","rene","sago","racy","have","yalu","glow","move","peps","hods","kins","salk","hand","cons","dare","myra","sega","type","mari","pelt","hula","gulf","jugs","flay","fest","spat","toms","zeno","taps","deny","swag","afro","baud","jabs","smut","egos","lara","toes","song","fray","luis","brut","olen","mere","ruff","slum","glad","buds","silt","rued","gelt","hive","teem","ides","sink","ands","wisp","omen","lyre","yuks","curb","loam","darn","liar","pugs","pane","carl","sang","scar","zeds","claw","berg","hits","mile","lite","khan","erik","slug","loon","dena","ruse","talk","tusk","gaol","tads","beds","sock","howe","gave","snob","ahab","part","meir","jell","stir","tels","spit","hash","omit","jinx","lyra","puck","laue","beep","eros","owed","cede","brew","slue","mitt","jest","lynx","wads","gena","dank","volt","gray","pony","veld","bask","fens","argo","work","taxi","afar","boon","lube","pass","lazy","mist","blot","mach","poky","rams","sits","rend","dome","pray","duck","hers","lure","keep","gory","chat","runt","jams","lays","posy","bats","hoff","rock","keri","raul","yves","lama","ramp","vote","jody","pock","gist","sass","iago","coos","rank","lowe","vows","koch","taco","jinn","juno","rape","band","aces","goal","huck","lila","tuft","swan","blab","leda","gems","hide","tack","porn","scum","frat","plum","duds","shad","arms","pare","chin","gain","knee","foot","line","dove","vera","jays","fund","reno","skid","boys","corn","gwyn","sash","weld","ruiz","dior","jess","leaf","pars","cote","zing","scat","nice","dart","only","owls","hike","trey","whys","ding","klan","ross","barb","ants","lean","dopy","hock","tour","grip","aldo","whim","prom","rear","dins","duff","dell","loch","lava","sung","yank","thar","curl","venn","blow","pomp","heat","trap","dali","nets","seen","gash","twig","dads","emmy","rhea","navy","haws","mite","bows","alas","ives","play","soon","doll","chum","ajar","foam","call","puke","kris","wily","came","ales","reef","raid","diet","prod","prut","loot","soar","coed","celt","seam","dray","lump","jags","nods","sole","kink","peso","howl","cost","tsar","uric","sore","woes","sewn","sake","cask","caps","burl","tame","bulk","neva","from","meet","webs","spar","fuck","buoy","wept","west","dual","pica","sold","seed","gads","riff","neck","deed","rudy","drop","vale","flit","romp","peak","jape","jews","fain","dens","hugo","elba","mink","town","clam","feud","fern","dung","newt","mime","deem","inti","gigs","sosa","lope","lard","cara","smug","lego","flex","doth","paar","moon","wren","tale","kant","eels","muck","toga","zens","lops","duet","coil","gall","teal","glib","muir","ails","boer","them","rake","conn","neat","frog","trip","coma","must","mono","lira","craw","sled","wear","toby","reel","hips","nate","pump","mont","died","moss","lair","jibe","oils","pied","hobs","cads","haze","muse","cogs","figs","cues","roes","whet","boru","cozy","amos","tans","news","hake","cots","boas","tutu","wavy","pipe","typo","albs","boom","dyke","wail","woke","ware","rita","fail","slab","owes","jane","rack","hell","lags","mend","mask","hume","wane","acne","team","holy","runs","exes","dole","trim","zola","trek","puma","wacs","veep","yaps","sums","lush","tubs","most","witt","bong","rule","hear","awry","sots","nils","bash","gasp","inch","pens","fies","juts","pate","vine","zulu","this","bare","veal","josh","reek","ours","cowl","club","farm","teat","coat","dish","fore","weft","exam","vlad","floe","beak","lane","ella","warp","goth","ming","pits","rent","tito","wish","amps","says","hawk","ways","punk","nark","cagy","east","paul","bose","solo","teed","text","hews","snip","lips","emit","orgy","icon","tuna","soul","kurd","clod","calk","aunt","bake","copy","acid","duse","kiln","spec","fans","bani","irma","pads","batu","logo","pack","oder","atop","funk","gide","bede","bibs","taut","guns","dana","puff","lyme","flat","lake","june","sets","gull","hops","earn","clip","fell","kama","seal","diaz","cite","chew","cuba","bury","yard","bank","byes","apia","cree","nosh","judo","walk","tape","taro","boot","cods","lade","cong","deft","slim","jeri","rile","park","aeon","fact","slow","goff","cane","earp","tart","does","acts","hope","cant","buts","shin","dude","ergo","mode","gene","lept","chen","beta","eden","pang","saab","fang","whir","cove","perk","fads","rugs","herb","putt","nous","vane","corm","stay","bids","vela","roof","isms","sics","gone","swum","wiry","cram","rink","pert","heap","sikh","dais","cell","peel","nuke","buss","rasp","none","slut","bent","dams","serb","dork","bays","kale","cora","wake","welt","rind","trot","sloe","pity","rout","eves","fats","furs","pogo","beth","hued","edam","iamb","glee","lute","keel","airy","easy","tire","rube","bogy","sine","chop","rood","elbe","mike","garb","jill","gaul","chit","dons","bars","ride","beck","toad","make","head","suds","pike","snot","swat","peed","same","gaza","lent","gait","gael","elks","hang","nerf","rosy","shut","glop","pain","dion","deaf","hero","doer","wost","wage","wash","pats","narc","ions","dice","quay","vied","eons","case","pour","urns","reva","rags","aden","bone","rang","aura","iraq","toot","rome","hals","megs","pond","john","yeps","pawl","warm","bird","tint","jowl","gibe","come","hold","pail","wipe","bike","rips","eery","kent","hims","inks","fink","mott","ices","macy","serf","keys","tarp","cops","sods","feet","tear","benz","buys","colo","boil","sews","enos","watt","pull","brag","cork","save","mint","feat","jamb","rubs","roxy","toys","nosy","yowl","tamp","lobs","foul","doom","sown","pigs","hemp","fame","boor","cube","tops","loco","lads","eyre","alta","aged","flop","pram","lesa","sawn","plow","aral","load","lied","pled","boob","bert","rows","zits","rick","hint","dido","fist","marc","wuss","node","smog","nora","shim","glut","bale","perl","what","tort","meek","brie","bind","cake","psst","dour","jove","tree","chip","stud","thou","mobs","sows","opts","diva","perm","wise","cuds","sols","alan","mild","pure","gail","wins","offs","nile","yelp","minn","tors","tran","homy","sadr","erse","nero","scab","finn","mich","turd","then","poem","noun","oxus","brow","door","saws","eben","wart","wand","rosa","left","lina","cabs","rapt","olin","suet","kalb","mans","dawn","riel","temp","chug","peal","drew","null","hath","many","took","fond","gate","sate","leak","zany","vans","mart","hess","home","long","dirk","bile","lace","moog","axes","zone","fork","duct","rico","rife","deep","tiny","hugh","bilk","waft","swig","pans","with","kern","busy","film","lulu","king","lord","veda","tray","legs","soot","ells","wasp","hunt","earl","ouch","diem","yell","pegs","blvd","polk","soda","zorn","liza","slop","week","kill","rusk","eric","sump","haul","rims","crop","blob","face","bins","read","care","pele","ritz","beau","golf","drip","dike","stab","jibs","hove","junk","hoax","tats","fief","quad","peat","ream","hats","root","flak","grit","clap","pugh","bosh","lock","mute","crow","iced","lisa","bela","fems","oxes","vies","gybe","huff","bull","cuss","sunk","pups","fobs","turf","sect","atom","debt","sane","writ","anon","mayo","aria","seer","thor","brim","gawk","jack","jazz","menu","yolk","surf","libs","lets","bans","toil","open","aced","poor","mess","wham","fran","gina","dote","love","mood","pale","reps","ines","shot","alar","twit","site","dill","yoga","sear","vamp","abel","lieu","cuff","orbs","rose","tank","gape","guam","adar","vole","your","dean","dear","hebe","crab","hump","mole","vase","rode","dash","sera","balk","lela","inca","gaea","bush","loud","pies","aide","blew","mien","side","kerr","ring","tess","prep","rant","lugs","hobo","joke","odds","yule","aida","true","pone","lode","nona","weep","coda","elmo","skim","wink","bras","pier","bung","pets","tabs","ryan","jock","body","sofa","joey","zion","mace","kick","vile","leno","bali","fart","that","redo","ills","jogs","pent","drub","slaw","tide","lena","seep","gyps","wave","amid","fear","ties","flan","wimp","kali","shun","crap","sage","rune","logs","cain","digs","abut","obit","paps","rids","fair","hack","huns","road","caws","curt","jute","fisk","fowl","duty","holt","miss","rude","vito","baal","ural","mann","mind","belt","clem","last","musk","roam","abed","days","bore","fuze","fall","pict","dump","dies","fiat","vent","pork","eyed","docs","rive","spas","rope","ariz","tout","game","jump","blur","anti","lisp","turn","sand","food","moos","hoop","saul","arch","fury","rise","diss","hubs","burs","grid","ilks","suns","flea","soil","lung","want","nola","fins","thud","kidd","juan","heps","nape","rash","burt","bump","tots","brit","mums","bole","shah","tees","skip","limb","umps","ache","arcs","raft","halo","luce","bahs","leta","conk","duos","siva","went","peek","sulk","reap","free","dubs","lang","toto","hasp","ball","rats","nair","myst","wang","snug","nash","laos","ante","opal","tina","pore","bite","haas","myth","yugo","foci","dent","bade","pear","mods","auto","shop","etch","lyly","curs","aron","slew","tyro","sack","wade","clio","gyro","butt","icky","char","itch","halt","gals","yang","tend","pact","bees","suit","puny","hows","nina","brno","oops","lick","sons","kilo","bust","nome","mona","dull","join","hour","papa","stag","bern","wove","lull","slip","laze","roil","alto","bath","buck","alma","anus","evil","dumb","oreo","rare","near","cure","isis","hill","kyle","pace","comb","nits","flip","clop","mort","thea","wall","kiel","judd","coop","dave","very","amie","blah","flub","talc","bold","fogy","idea","prof","horn","shoo","aped","pins","helm","wees","beer","womb","clue","alba","aloe","fine","bard","limo","shaw","pint","swim","dust","indy","hale","cats","troy","wens","luke","vern","deli","both","brig","daub","sara","sued","bier","noel","olga","dupe","look","pisa","knox","murk","dame","matt","gold","jame","toge","luck","peck","tass","calf","pill","wore","wadi","thur","parr","maul","tzar","ones","lees","dark","fake","bast","zoom","here","moro","wine","bums","cows","jean","palm","fume","plop","help","tuba","leap","cans","back","avid","lice","lust","polo","dory","stew","kate","rama","coke","bled","mugs","ajax","arts","drug","pena","cody","hole","sean","deck","guts","kong","bate","pitt","como","lyle","siam","rook","baby","jigs","bret","bark","lori","reba","sups","made","buzz","gnaw","alps","clay","post","viol","dina","card","lana","doff","yups","tons","live","kids","pair","yawl","name","oven","sirs","gyms","prig","down","leos","noon","nibs","cook","safe","cobb","raja","awes","sari","nerd","fold","lots","pete","deal","bias","zeal","girl","rage","cool","gout","whey","soak","thaw","bear","wing","nagy","well","oink","sven","kurt","etna","held","wood","high","feta","twee","ford","cave","knot","tory","ibis","yaks","vets","foxy","sank","cone","pius","tall","seem","wool","flap","gird","lore","coot","mewl","sere","real","puts","sell","nuts","foil","lilt","saga","heft","dyed","goat","spew","daze","frye","adds","glen","tojo","pixy","gobi","stop","tile","hiss","shed","hahn","baku","ahas","sill","swap","also","carr","manx","lime","debs","moat","eked","bola","pods","coon","lacy","tube","minx","buff","pres","clew","gaff","flee","burn","whom","cola","fret","purl","wick","wigs","donn","guys","toni","oxen","wite","vial","spam","huts","vats","lima","core","eula","thad","peon","erie","oats","boyd","cued","olaf","tams","secs","urey","wile","penn","bred","rill","vary","sues","mail","feds","aves","code","beam","reed","neil","hark","pols","gris","gods","mesa","test","coup","heed","dora","hied","tune","doze","pews","oaks","bloc","tips","maid","goof","four","woof","silo","bray","zest","kiss","yong","file","hilt","iris","tuns","lily","ears","pant","jury","taft","data","gild","pick","kook","colt","bohr","anal","asps","babe","bach","mash","biko","bowl","huey","jilt","goes","guff","bend","nike","tami","gosh","tike","gees","urge","path","bony","jude","lynn","lois","teas","dunn","elul","bonn","moms","bugs","slay","yeah","loan","hulk","lows","damn","nell","jung","avis","mane","waco","loin","knob","tyke","anna","hire","luau","tidy","nuns","pots","quid","exec","hans","hera","hush","shag","scot","moan","wald","ursa","lorn","hunk","loft","yore","alum","mows","slog","emma","spud","rice","worn","erma","need","bags","lark","kirk","pooh","dyes","area","dime","luvs","foch","refs","cast","alit","tugs","even","role","toed","caph","nigh","sony","bide","robs","folk","daft","past","blue","flaw","sana","fits","barr","riot","dots","lamp","cock","fibs","harp","tent","hate","mali","togs","gear","tues","bass","pros","numb","emus","hare","fate","wife","mean","pink","dune","ares","dine","oily","tony","czar","spay","push","glum","till","moth","glue","dive","scad","pops","woks","andy","leah","cusp","hair","alex","vibe","bulb","boll","firm","joys","tara","cole","levy","owen","chow","rump","jail","lapp","beet","slap","kith","more","maps","bond","hick","opus","rust","wist","shat","phil","snow","lott","lora","cary","mote","rift","oust","klee","goad","pith","heep","lupe","ivan","mimi","bald","fuse","cuts","lens","leer","eyry","know","razz","tare","pals","geek","greg","teen","clef","wags","weal","each","haft","nova","waif","rate","katy","yale","dale","leas","axum","quiz","pawn","fend","capt","laws","city","chad","coal","nail","zaps","sort","loci","less","spur","note","foes","fags","gulp","snap","bogs","wrap","dane","melt","ease","felt","shea","calm","star","swam","aery","year","plan","odin","curd","mira","mops","shit","davy","apes","inky","hues","lome","bits","vila","show","best","mice","gins","next","roan","ymir","mars","oman","wild","heal","plus","erin","rave","robe","fast","hutu","aver","jodi","alms","yams","zero","revs","wean","chic","self","jeep","jobs","waxy","duel","seek","spot","raps","pimp","adan","slam","tool","morn","futz","ewes","errs","knit","rung","kans","muff","huhs","tows","lest","meal","azov","gnus","agar","sips","sway","otis","tone","tate","epic","trio","tics","fade","lear","owns","robt","weds","five","lyon","terr","arno","mama","grey","disk","sept","sire","bart","saps","whoa","turk","stow","pyle","joni","zinc","negs","task","leif","ribs","malt","nine","bunt","grin","dona","nope","hams","some","molt","smit","sacs","joan","slav","lady","base","heck","list","take","herd","will","nubs","burg","hugs","peru","coif","zoos","nick","idol","levi","grub","roth","adam","elma","tags","tote","yaws","cali","mete","lula","cubs","prim","luna","jolt","span","pita","dodo","puss","deer","term","dolt","goon","gary","yarn","aims","just","rena","tine","cyst","meld","loki","wong","were","hung","maze","arid","cars","wolf","marx","faye","eave","raga","flow","neal","lone","anne","cage","tied","tilt","soto","opel","date","buns","dorm","kane","akin","ewer","drab","thai","jeer","grad","berm","rods","saki","grus","vast","late","lint","mule","risk","labs","snit","gala","find","spin","ired","slot","oafs","lies","mews","wino","milk","bout","onus","tram","jaws","peas","cleo","seat","gums","cold","vang","dewy","hood","rush","mack","yuan","odes","boos","jami","mare","plot","swab","borg","hays","form","mesh","mani","fife","good","gram","lion","myna","moor","skin","posh","burr","rime","done","ruts","pays","stem","ting","arty","slag","iron","ayes","stub","oral","gets","chid","yens","snub","ages","wide","bail","verb","lamb","bomb","army","yoke","gels","tits","bork","mils","nary","barn","hype","odom","avon","hewn","rios","cams","tact","boss","oleo","duke","eris","gwen","elms","deon","sims","quit","nest","font","dues","yeas","zeta","bevy","gent","torn","cups","worm","baum","axon","purr","vise","grew","govs","meat","chef","rest","lame"]
]
answers = [
    [["hit", "hot", "lot", "log", "cog"], ["hit", "hot", "dot", "dog", "cog"]],
    [],
    [["a", "c"]],
    [["qa","pa","pt","st","sq"],["qa","la","lt","st","sq"],["qa","ma","mt","st","sq"],["qa","ca","cr","sr","sq"],["qa","la","lr","sr","sq"],["qa","fa","fr","sr","sq"],["qa","ba","br","sr","sq"],["qa","ma","mr","sr","sq"],["qa","ca","ci","si","sq"],["qa","na","ni","si","sq"],["qa","la","li","si","sq"],["qa","ta","ti","si","sq"],["qa","pa","pi","si","sq"],["qa","ba","bi","si","sq"],["qa","ha","hi","si","sq"],["qa","ma","mi","si","sq"],["qa","pa","ph","sh","sq"],["qa","ra","rh","sh","sq"],["qa","ta","th","sh","sq"],["qa","ca","co","so","sq"],["qa","ga","go","so","sq"],["qa","ta","to","so","sq"],["qa","na","no","so","sq"],["qa","la","lo","so","sq"],["qa","pa","po","so","sq"],["qa","ya","yo","so","sq"],["qa","ma","mo","so","sq"],["qa","ha","ho","so","sq"],["qa","la","ln","sn","sq"],["qa","ra","rn","sn","sq"],["qa","ma","mn","sn","sq"],["qa","ca","cm","sm","sq"],["qa","ta","tm","sm","sq"],["qa","pa","pm","sm","sq"],["qa","fa","fm","sm","sq"],["qa","ta","tc","sc","sq"],["qa","na","nb","sb","sq"],["qa","pa","pb","sb","sq"],["qa","ra","rb","sb","sq"],["qa","ya","yb","sb","sq"],["qa","ma","mb","sb","sq"],["qa","ta","tb","sb","sq"],["qa","ga","ge","se","sq"],["qa","la","le","se","sq"],["qa","na","ne","se","sq"],["qa","ra","re","se","sq"],["qa","ba","be","se","sq"],["qa","ya","ye","se","sq"],["qa","fa","fe","se","sq"],["qa","ha","he","se","sq"],["qa","ma","me","se","sq"]],
    [["hot", "dot", "dog"]],
    [],
    [["sand","sans","sins","sims","aims","arms","arts","ants","ante","anne","acne"],["sand","sans","kans","kins","kids","aids","ands","ants","ante","anne","acne"],["sand","sans","sins","kins","kids","aids","ands","ants","ante","anne","acne"],["sand","sane","sine","side","aide","aids","ands","ants","ante","anne","acne"],["sand","sane","sade","side","aide","aids","ands","ants","ante","anne","acne"],["sand","sans","sins","sirs","airs","aids","ands","ants","ante","anne","acne"],["sand","sans","sins","sims","aims","aids","ands","ants","ante","anne","acne"],["sand","sans","bans","bins","bids","aids","ands","ants","ante","anne","acne"],["sand","band","bans","bins","bids","aids","ands","ants","ante","anne","acne"],["sand","sans","sins","bins","bids","aids","ands","ants","ante","anne","acne"],["sand","band","bind","bins","bids","aids","ands","ants","ante","anne","acne"]]
]

tot_time = 0
iterations = 1
for i in range(iterations):
    print("\nIteration {}".format(i))
    print("================================")
    for beginWord, endWord, wordList, answer in zip(beginWords, endWords, wordLists, answers):
        tic = time()
        sol = Solution().findLadders(beginWord, endWord, wordList)
        toc = time()
        sol_set = {tuple(path) for path in sol}
        ans_set = {tuple(path) for path in answer}
        print(len(sol_set.intersection(ans_set)), "/", len(ans_set), "\t({:.4} sec)".format(toc-tic))
        tot_time += toc-tic
baseline_time = 2.5 * (iterations/100)
print("\nTotal time = {:.3f}; {:.3f} of baseline".format(tot_time, tot_time/baseline_time))
