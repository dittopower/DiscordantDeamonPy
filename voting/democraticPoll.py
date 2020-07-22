import discord
from voting.voteOption import voteOption


class democraticPoll:
    votes = {}
    open = True
    id = -1

    def __init__(self, creator: discord.User, question: str, multivote=False, locked=False, opts: [str] = []):
        self.owner = creator
        self.question = question
        self.options = []
        for o in opts:
            self.options.append(voteOption(creator, opts[o]))
        self.multivote = multivote
        self.locked = locked

    def addOption(self, author: discord.User, option: str) -> bool:
        return self.addOption2(voteOption(author, option))

    def addOption2(self, option: voteOption) -> bool:
        if self.locked:
            return False
        else:
            self.options.append(option)
            return True
    
    def start(self):
        self.open = True
        self.votes = {}

    def finish(self):
        if self.open:
            self.open = False
            for option in self.options:
                option.count = 0
            if self.multivote:
                for voter in self.votes:
                    for vote in self.votes[voter]:
                        self.options[vote] += 1
            else:
                for voter in self.votes:
                    self.options[self.votes[voter]].count += 1
        results = "Results: %{0.id} {0.question}:\n{1}".format(self,self.listOptions(True))
        return results

    def listOptions(self, includeResults=False) -> str:
        res = []
        for i in range(len(self.options)):
            count = ""
            if includeResults:
                count = "votes: {0}".format(self.options[i].count)
            res.append("- {0}: {1} {2}".format(i, self.options[i].option, count))
        return "\n".join(res)

    def status(self) -> str:
        out = "The poll {0.question}:".format(self)
        if self.locked:
            out += "\n- is editable"
        if self.multivote:
            out += "\n- Allow multiple votes"
        if self.open:
            out += "\n- is accepting votes"
        else:
            out += "\n- is not accepting votes"
        return out

    async def vote(self, voter: discord.User, optionIndex: int):
        if self.open:
            if optionIndex <= len(self.options):
                if self.multivote:
                    myVotes = self.votes.get(voter, {})
                    myVotes[optionIndex] = True
                    self.votes[voter] = myVotes
                else:
                    myVote = self.votes.get(voter)
                    if myVote:
                        self.options[myVote].count -= 1
                    self.votes[voter] = optionIndex
                self.options[optionIndex].count += 1
                return await voter.send("You voted for '{0}' in poll %{1.id} '{1.question}'".format(self.options[optionIndex].option, self))
            else:
                return await voter.send("Invalid vote! '{0}' is not a recognised option in poll %{1.id} '{1.question}'.".format(optionIndex, self))
        else:
            return await voter.send("The poll %{0.id} '{0.question}' is not accepting votes currently.".format(self))
