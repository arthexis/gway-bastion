# Bastion deployment status contract (schema 1)

The Ansible installer **stages only**. It atomically writes
`<root>/deployment/staged.json` after copying the release files and writing
`<root>/releases/<sha>/REVISION`. The staged record is owned by the same
account that installs the release (root under the production /opt path), mode 0644.
Ansible's copy module uses a temporary file and atomic replacement by default.
Repeat staging of the same revision does not change the record.

Record shape: `{"schema":1,"revision":"<40 lowercase hex SHA>"}`.
An eventual **separate, explicitly authorized activation workflow** may write
`deployment/activated.json` only after verified activation, with the same
schema and atomicity. The staging installer MUST NOT create or modify it.

Run `python3 deployment_status.py` (optionally set `BASTION_INSTALL_ROOT`).
It only reads metadata. Outputs JSON:
- `staged`: staged release verified, no activation evidence; runtime `not_applicable`.
- `activated`: activation evidence and immutable revision verified; runtime
  `unknown` until an independently verified runtime probe is designed.
- `unknown`: no evidence or inconsistent/malformed evidence. Invalid evidence
  produces exit status 2; neither staged nor activated implies a healthy service.

Consumers MUST NOT interpret `staged` as installed/active/healthy.
No secret, SSH-agent, USB, udev, sudoers or service operations are involved.
