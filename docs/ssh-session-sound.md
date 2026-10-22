# SSH session sound (opt-in)

This feature announces a newly opened SSH PAM session through the shared
`gway-lcd-sound` dispatcher. It is deliberately **not active** after staging a
Bastion release: `deploy.sh` does not install or activate the helper, edit
`/etc/pam.d/sshd`, reload SSH, or create sound state.

The helper accepts only `PAM_TYPE=open_session` from the `sshd` PAM service. It
does not log user names, remote addresses, commands, or authentication data. It
uses a root-owned runtime marker to limit announcements to one every 60 seconds,
then starts the shared `ssh/session-opened` event asynchronously as the normal
GWAY user. A missing sound installation or playback failure is silent and never
denies or delays login.

## Controlled field activation

Activation changes the SSH authentication path and needs separate operator
approval on the target host.

1. Confirm the installed `gway-lcd-sound` release resolves
   `ssh/session-opened` to `notice`; do not create an ad-hoc GPIO player.
2. Back up `/etc/pam.d/sshd` with its owner and mode preserved. Install the
   reviewed helper as `/usr/local/libexec/bastion-ssh-session-sound`, root-owned
   and mode `0755`.
3. Add the single line from `config/pam.d/sshd-gway-session-sound.conf` after
   the existing `common-session` include in `/etc/pam.d/sshd`. Do not replace
   the PAM file or edit unrelated authentication rules.
4. Keep an existing administrative SSH session open. Establish one new test
   session, confirm login succeeds, then confirm the bounded sound behavior.
5. Roll back by restoring the backed-up `/etc/pam.d/sshd` before ending the
   retained administrative session. The PAM change applies to future sessions;
   no SSH daemon restart is required.

Do not use this hook to authorize access or infer Bastion USB/key state. It is
only an operator-awareness cue.
