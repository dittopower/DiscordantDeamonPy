import discord
import tinydb
import re
import poll as polllib
from auth import AuthManager


class PollManager:
    commandWords = {"vote": "vote"}
    _tableName = "polls"

    def __init__(self, db: tinydb.TinyDB, auth: AuthManager):
        self.table = db.table(self._tableName)
        self.auth = auth

    async def processMessage(self, message: discord.Message):
        author: int = message.author
        authorId: int = message.author.id
        # Remove command prefix
        msg = re.sub("^.*"+self.commandWords.get("vote"), "", message.content, 1).strip()

        # get current command option
        cmd = msg.split(" ", 1) + [""]
        cmdoption = cmd[0].lower()
        cmdargs = cmd[1]

        # Create a new poll
        if cmdoption.startswith("new") or cmdoption.startswith("create"):
            multivote: bool = False
            editable: bool = True
            showAuthors: bool = False
            showVotes: bool = False
            canVoteNow: bool = True
            question: str = ""
            options: [] = []
            poll = polllib.Poll(authorId, question, multivote, editable, showVotes, showAuthors, canVoteNow, options)
            id = self.table.insert(poll.getDataObject())
            return await message.channel.send('Poll created: ||%{0}|| {1.question}'.format(id, poll))

        # Show all polls
        if cmdoption.startswith("history"):
            output = "Historical Polls:"
            output += "\n-----------------"
            polls = self.table.all()
            for poll in polls:
                output += "\n\|\| ||%{0.doc_id}|| \|\| {0[question]}".format(poll)
            output += "\n-----------------"
            return await message.channel.send(output)

        # Show current polls
        if cmdoption.startswith("current") or cmdoption.startswith("active"):
            output = "Current Polls:"
            output += "\n-----------------"
            qry = tinydb.Query()
            polls = self.table.search(qry._finished == False)
            for poll in polls:
                output += "\n\|\| ||%{0.doc_id}|| \|\| {0[question]}".format(poll)
            output += "\n-----------------"
            return await message.channel.send(output)

        # Perform an operation for an existing poll
        # Allow % prefix or no prefix
        if cmdoption.startswith("%"):
            cmdoption = cmdoption.replace("%", "")
        if cmdoption.isnumeric():
            pollobj = self.table.get(doc_id=int(cmdoption))

            # Verify a poll was found
            if not pollobj:
                return await message.channel.send('Unknown Poll ID!')
            poll = self.pollFrom(pollobj)

            # get subcommand option and args
            cmd = cmdargs.split(" ", 1) + [""]
            cmdoption = cmd[0].lower()
            cmdargs = cmd[1]

            # add an option to the poll
            if cmdoption.startswith("add"):
                if poll.addOption(authorId, cmdargs):
                    self.table.update(poll.getDataObject(),None,[pollobj.doc_id])
                    return await message.channel.send('Added option {1} to ||%{0.doc_id}|| {0[question]}'.format(pollobj, cmdargs))
                else:
                    return await message.channel.send("Couldn't add option {1} to ||%{0.id}|| {0.question}. The poll may not allow editing.".format(poll, cmdargs))

            # TODO: remove option

            # TODO: edit option

            # Vote for an option
            if cmdoption.isnumeric():
                poll.vote(authorId, int(cmdoption))
                self.table.update(poll.getDataObject(),None,[pollobj.doc_id])
                return await message.channel.send("TODO")  # TODO: response

            # Display the status of the poll
            if cmdoption.startswith("status"):
                return await message.channel.send(poll.status())

            # list the options of the poll
            if cmdoption.startswith("list"):
                return await message.channel.send("Poll ||%{0.doc_id}|| {0[question]}:\n".format(pollobj) + poll.listOptions())

            # Display the current results of the poll
            if cmdoption.startswith("results") or cmdoption.startswith("tally"):
                return await message.channel.send("Poll ||%{0.doc_id}|| {0[question]}:\n{1}".format(pollobj, poll.listOptions(True)))

            # Create a new instance of an existing poll
            if cmdoption.startswith("redo"):
                poll = poll.redo(authorId)
                id = self.table.insert(poll.getDataObject())
                return await message.channel.send('Recreated: {0}\n{1}'.format(poll.status(), poll.listOptions()))

            # Admin & poll owner commands
            if self.auth.isBotAdmin(authorId) or author.permissions_in(message.channel).administrator or authorId is poll.owner:
                # Delete the poll
                if cmdoption.startswith("delete"):
                    self.table.remove(doc_ids=pollobj.doc_id)
                    return await message.channel.send('Poll deleted: ||%{0.id}|| {0.question}'.format(poll))

                # TODO: edit the poll question

                # TODO: reset a running poll
                if cmdoption.startswith("start") or cmdoption.startswith("restart"):
                    poll.start()
                    # TODO: update msg
                    self.table.update(poll.getDataObject(),None,[pollobj.doc_id])
                    return await message.channel.send('Poll: ||%{0.id}|| {0.question}\n{1}\n----\nPlease vote now: msg me "~vote ||%{0.id}|| your_options_number"'.format(poll, poll.listOptions()))

                # Restart a finished poll
                if cmdoption.startswith("start") or cmdoption.startswith("restart"):
                    poll.reset()
                    # TODO: update msg
                    self.table.update(poll.getDataObject(),None,[pollobj.doc_id])
                    return await message.channel.send('Poll: ||%{0.id}|| {0.question}\n{1}\n----\nPlease vote now: msg me "~vote ||%{0.id}|| your_options_number"'.format(poll, poll.listOptions()))

                # End a running poll
                if cmdoption.startswith("finish") or cmdoption.startswith("end"):
                    # TODO: update msg
                    out = poll.finish()
                    self.table.update(poll.getDataObject(),None,[pollobj.doc_id])
                    return await message.channel.send(out)

        # No matching commands options found.
        return await message.channel.send('Looks like your vote command was incomplete or invalid! "{0}"'.format(message.content))

    def pollFrom(self, dicti: dict):
        poll = polllib.Poll(-1, "Null")
        poll.setDataObject(dicti)
        return poll
