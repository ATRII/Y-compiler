r'LR1 grammar parser'

from queue import Queue, LifoQueue
import token


class LOADER:
    def __init__(self) -> None:
        pass

    def loadgrammarfile(self, grammar_dir: str):
        ans = {}
        f = open(grammar_dir, "r")
        fline = f.readline()
        st = fline.strip()
        lines = f.readlines()
        f.close()
        for line in lines:
            l, r = line.split('::=')
            l = l.strip()
            rlist = r.split('|')
            for e in rlist:
                if l not in ans:
                    ans[l] = set()
                e_processed = e.strip().split()
                if e_processed == ['epsilon']:
                    ans[l].add(tuple())
                else:
                    ans[l].add(tuple(e_processed))
        return st, ans


class LR1:
    def __init__(self, startstate: str, transtable: dict) -> None:
        self.startstate = startstate
        self.expandedstartstate = self.startstate[0:-1]+'_>'
        self.start = (self.expandedstartstate,
                      (self.startstate,), frozenset(['#']), 0)
        self.transtable = transtable
        self.prodnum = self.calpnum()
        self.production = {v: k for k, v in self.prodnum.items()}
        self.nonterminal = set(transtable.keys())
        self.terminal = set([i for x in transtable.values()
                            for j in x for i in j if i not in self.nonterminal])
        self.terminal.add('#')
        self.symbols = self.nonterminal.union(self.terminal)
        self.epsilon = 'epsilon'
        self.nullable = self.calnull()
        self.symbolfirst()
        self.transtable[self.expandedstartstate] = set((self.startstate,))
        self.buildprojects()
        self.parsertable()

    def calpnum(self) -> dict:
        ans = {}
        cnt = 0
        for i in self.transtable:
            for p in self.transtable[i]:
                ans[(i, p)] = cnt
                cnt += 1
        return ans

    def calnull(self) -> set:
        ans, cnt = set(), set()
        q = Queue()
        for s in self.nonterminal:
            q.put(s)
        while not q.empty():
            e = q.get()
            end = 0
            # print(cnt)
            for p in self.transtable[e]:
                if len(p) == 0:
                    ans.add(e)
                    cnt.add(e)
                    break
                else:
                    flag = 1  # nullable
                    for c in p:
                        if c in self.terminal:
                            flag = 0
                            break
                        elif c in self.nonterminal:
                            if c == e:
                                continue
                            if c in cnt:
                                if c not in ans:
                                    flag = 0
                                    break
                            else:
                                q.put(e)
                                end = 1
                                break
                    if end:
                        break
                    if flag:
                        ans.add(e)
                    cnt.add(e)
        return ans

    def symbolfirst(self):
        self.first = {symbol: set() for symbol in self.symbols}
        for terminal in self.terminal:
            self.first[terminal] = {terminal}
        cnt = set()
        q = Queue()
        for nonterminal in self.nonterminal:
            q.put(nonterminal)
        while not q.empty():
            # print(q.queue)
            nonterminal = q.get()
            flag = 1
            for production in self.transtable[nonterminal]:
                for symbol in production:
                    if symbol in self.terminal:
                        self.first[nonterminal].add(symbol)
                        break
                    else:
                        if symbol == nonterminal:
                            continue
                        if symbol not in cnt:
                            flag = 0
                            q.put(nonterminal)
                            break
                        self.first[nonterminal].update(
                            self.first[symbol]-set([self.epsilon]))
                        if symbol not in self.nullable:
                            break
            if nonterminal in self.nullable:
                self.first[nonterminal].add(self.epsilon)
            if flag:
                cnt.add(nonterminal)
# TODO:unknown error

    def compute_first(self, symbol_list: tuple) -> set():
        first = set()
        for symbol in symbol_list:
            if symbol in self.terminal:
                first.add(symbol)
                break
            else:
                first.update(self.first[symbol]-set([self.epsilon]))
                if symbol not in self.nullable:
                    break
        if all([i in self.nullable for i in symbol_list]):
            first.add(self.epsilon)
        return first

    def firstset(self, t: tuple, s: set) -> frozenset:
        ans = set()
        for i in s:
            ss = t+(i,)
            ans = ans.union(self.compute_first(ss))
        return frozenset(ans)

    def closure(self, plist: set) -> frozenset:
        ans = set()
        q = Queue()

        for p in plist:
            q.put(p)
            ans.add(p)
        while not q.empty():
            p = q.get()
            # print(p)
            if p[-1] >= len(p[1]):
                continue
            if p[1][p[-1]] in self.nonterminal:
                for x in self.transtable[p[1][p[-1]]]:
                    new = (p[1][p[-1]], x,
                           self.firstset(p[1][p[-1]+1:], p[2]), 0)
                    if new in ans:
                        continue
                    ans.add(new)
                    # print(new)
                    q.put(new)
        return frozenset(ans)

    def go(self, s: frozenset, c: str) -> frozenset:
        ans = set()
        for i in s:
            if i[-1] >= len(i[1]):
                continue
            else:
                if c == i[1][i[-1]]:
                    ans.add((i[0], i[1], i[2], i[-1]+1))
        return self.closure(ans)

    def buildprojects(self) -> None:
        # (start state, production, forward, position)
        self.projectsmap = {}  # trans
        self.projects = {}  # name
        cnt = 0
        q = Queue()
        x = self.closure([self.start])
        self.projects[x] = 'I'+str(cnt)
        self.projectsmap['I'+str(cnt)] = {}
        cnt += 1
        q.put(x)
        while not q.empty():
            s = q.get()
            for i in s:
                # print(i)
                if i[-1] >= len(i[1]):
                    continue
                else:
                    c = i[1][i[-1]]
                    nxt = self.go(s, c)
                    # print(c, nxt)
                    if nxt not in self.projects:
                        self.projectsmap[self.projects[s]][c] = 'I'+str(cnt)
                        self.projectsmap['I'+str(cnt)] = {}
                        self.projects[nxt] = 'I'+str(cnt)
                        cnt += 1
                        q.put(nxt)
                    else:
                        self.projectsmap[self.projects[s]
                                         ][c] = self.projects[nxt]

    def parsertable(self) -> None:
        self.action, self.goto = {}, {}
        # project
        for p in self.projects:
            # print(p)
            self.action[self.projects[p]] = {}
            self.goto[self.projects[p]] = {}
            # production
            for i in p:
                if i[-1] >= len(i[1]):
                    if i == (self.expandedstartstate, (self.startstate,), frozenset(['#']), 1):
                        self.action[self.projects[p]]['#'] = 'acc'
                    else:
                        for a in i[2]:
                            # if i[0] == '<parameter_list>':
                            # print(self.projects[p], a)
                            self.action[self.projects[p]][a] = 'r' + \
                                str(self.prodnum[(i[0], i[1])])
                else:
                    c = i[1][i[-1]]
                    # print(i)
                    if c in self.terminal:
                        Ik = self.projects[p]
                        Ij = self.projectsmap[Ik][c]
                        self.action[Ik][c] = 'S' + Ij[1:]
                    else:
                        Ik = self.projects[p]
                        # print(Ik, c, sep=', ')
                        Ij = self.projectsmap[Ik][c]
                        self.goto[Ik][c] = Ij

    def parsertablelist(self) -> list:
        tr0 = ['state']+['action']+[''] * \
            (len(self.terminal-{self.epsilon})-1) + \
            ['goto']+['']*(len(self.nonterminal)-1)
        ans = [tr0]
        tr1 = ['']
        for t in self.terminal:
            if t != self.epsilon:
                tr1.append(t)
        for t in self.nonterminal:
            tr1.append(t)
        ans.append(tr1)
        for i in self.action:
            tr = [i]
            for t in self.terminal:
                if t == self.epsilon:
                    continue
                if t not in self.action[i]:
                    tr.append('')
                else:
                    tr.append(self.action[i][t])
            for t in self.nonterminal:
                if t not in self.goto[i]:
                    tr.append('')
                else:
                    tr.append(self.goto[i][t])
            ans.append(tr)
        return ans

    def run(self, s: list):
        inputq = Queue()
        pstk, statestk = LifoQueue(), LifoQueue()
        pstklist, statestklist = [], []
        statestk.put('I0')
        pstklist.append(pstk.queue.copy())
        statestklist.append(statestk.queue.copy())
        for i in s:
            inputq.put(i)
        inputq.put((0, '#', '#'))
        while not inputq.empty():
            c_t = inputq.queue[0]
            c = c_t[1]
            if c == '#' and len(pstk.queue) == 1:
                return True, pstklist, statestklist
            state = statestk.queue[-1]
            if c not in self.action[state]:
                print("unexpected token \"{0}\" at row{1}, type {2}, runtime statestack {3}, parserstack {4}".format(
                    c_t[2], c_t[0], c_t[1], statestk.queue, pstk.queue))
                fe = open('../result/grammar_error.log', 'w+')
                fe.write("unexpected token \"{0}\" at row{1}, type {2}, runtime statestack {3}, parserstack {4}".format(
                    c_t[2], c_t[0], c_t[1], statestk.queue, pstk.queue))
                fe.close()
                break
            task = self.action[state][c]
            if task[0] == 'S':
                inputq.get()
                pstk.put(c)
                statestk.put('I'+task[1:])
                pstklist.append(pstk.queue.copy())
                statestklist.append(statestk.queue.copy())
                # print(task, pstk.queue)
            elif task[0] == 'r':
                pro = self.production[int(task[1:])]
                l = len(pro[1])
                for i in range(l):
                    if pstk.empty():
                        print("ERROR: praser stack empty")
                        return False, pstklist, statestklist
                    if statestk.empty():
                        print("ERROR: state stack empty")
                        return False, pstklist, statestklist
                    element = pstk.get()
                    statestk.get()
                    if element != pro[1][l-i-1]:
                        print("ERROR: praser stack error")
                        return False, pstklist, statestklist
                pstk.put(pro[0])
                statestk.put(self.goto[statestk.queue[-1]][pro[0]])
                pstklist.append(pstk.queue.copy())
                statestklist.append(statestk.queue.copy())
                # print(task, pstk.queue)

        return False, pstklist, statestklist


class PARSER:
    def __init__(self, grammar_dir: str) -> None:
        self.grammar_dir = grammar_dir
        self.l = LOADER()
        start, trans = self.l.loadgrammarfile(self.grammar_dir)
        self.lr1 = LR1(start, trans)

    def parse(self, tokenlist: list):
        return self.lr1.run(tokenlist)
