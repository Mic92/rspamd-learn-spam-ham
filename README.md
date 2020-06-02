## rspam-learn-spam-ham

Teach rspamd about spam/non-spam based on the emails that are marked as read.
Read emails in folder called "spam" are treated as SPAM.
Other read emails are treated as ham.

## USAGE

```
$ nix-build
$ ./result/bin/update-spam-ham ./path/to/maidir https://rspamd.<yourdomain>.<tld> "Your password"
```
