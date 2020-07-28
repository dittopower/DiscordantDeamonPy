import discord
import pollOption
import copy


class Poll:

    def __init__(self, author: int, question: str, multivote=False, editable=False, publicVotes=False, publicAuthors=False, voteable=False, opts: [str] = []):
        self._author = author
        self._question = question
        self._options = []
        for o in opts:
            self._options.append(pollOption.Option(author, opts[o]))
        self._multivote = multivote
        self._editable = editable
        self._voteable = voteable
        self._publicVotes = publicVotes
        self._publicAuthors = publicAuthors
        self._finished = False
        self._votes = {}

    def redo(self, author: int):
        poll = copy.copy(self)
        poll._author = author
        return poll

    def start(self):
        if not self._finished:
            self._voteable = True
            self._votes = {}
            return True
        else:
            # TODO: throw error
            False

    def reset(self):
        self._finished = False
        self.start()

    def count(self):
        totals = [0] * len(self._options)
        if self._multivote:
            for votes in self._votes.values():
                for vote in votes:
                    totals[vote] += 1
        else:
            for vote in self._votes.values():
                totals[vote] += 1
        return totals

    def finish(self):
        if self._finished:
            self._finished = True
        return "{0.question}:\n{1}".format(self, self.listOptions(True))

    def status(self) -> str:
        out = "The poll %{0.id} {0.question}:".format(self)
        if self._editable:
            out += "\n✅ is editable"
        if self._multivote:
            out += "\n🔢 Allows multiple votes each"
        else:
            out += "\n1️⃣ Allows one vote each"
        if self._voteable:
            out += "\n✅ is accepting votes"
        else:
            out += "\n❌ is not accepting votes"
        return out

    def setQuestion(self, question: str):
        if self._editable:
            self._question = question
        else:
            # TODO: error
            False

    def setMultiVote(self, multi: bool):
        if self._editable:
            self._multivote = multi
        else:
            # TODO: error
            False

    def listOptions(self, includeResults=False) -> str:
        res = []
        if includeResults:
            results = self.count()
        for i in range(len(self._options)):
            count = ""
            if includeResults:
                count = "votes: {0}".format(results[i])
            res.append("- {0}: {1} {2}".format(i, self._options[i].option, count))
        return "\n".join(res)

    def addOption(self, author: int, option: str) -> bool:
        if self._editable:
            self._options.append(pollOption.Option(author, option))
            return True
        else:
            # TODO: throw error
            False

    def editOption(self, author: int, id: int, option: str) -> bool:
        if self._editable:
            if len(self._options) <= id:
                self._options[id].option = option
                if author not in self._options[id].authors:
                    self._options[id].authors.append(author)
                return True
            else:
                # TODO: error
                False
        else:
            # TODO: throw error
            False

    def deleteOption(self, id: int) -> bool:
        if self._editable:
            if len(self._options) <= id:
                self._options.pop(id)
                return True
            else:
                # TODO: throw error
                False
        else:
            # TODO: throw error
            False

    def vote(self, voter: int, optionIndex: int):
        if not self._finished:
            if optionIndex <= len(self._options):
                if self._multivote:
                    myVotes = self._votes.get(voter, {})
                    myVotes[optionIndex] = True
                    self._votes[voter] = myVotes
                else:
                    self._votes[voter] = optionIndex
                return True
            else:
                # TODO: throw error
                False
        else:
            # TODO: throw error
            False

    def unvote(self, voter: int, optionIndex: int):
        if not self._finished:
            if optionIndex <= len(self._options):
                if self._multivote:
                    myVotes: dict = self._votes.get(voter)
                    if myVotes and optionIndex in myVotes:
                        myVotes.pop(optionIndex)
                        self._votes[voter] = myVotes
                else:
                    if self._votes[voter] == optionIndex:
                        self._votes.pop(voter)
                return True
            else:
                # TODO: throw error
                False
        else:
            # TODO: throw error
            False
