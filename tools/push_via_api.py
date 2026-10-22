"""通过 GitHub Git Data API 推送本地提交（github.com:443 被代理拦截时的备用通道）。

用法:
    set GH_TOKEN=ghp_xxxx            # 需要对目标仓库有 push 权限的 token
    python tools/push_via_api.py <owner/repo> <branch> <base_sha> <tip_sha>

例（把本地最近一笔推上远端）:
    python tools/push_via_api.py 18162319926/ejee-desktop-pet main <远程tip> <本地HEAD>

只重放 base_sha..tip_sha 之间的提交，逐个上传 blob / 建 tree / 建 commit，
最后 PATCH 分支 ref。尽量复现本地 commit sha（author/committer 时间原样带上）。
正常 `git push` 能通时不要用本脚本。
"""
import base64
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request

REPO = sys.argv[1]
BRANCH = sys.argv[2]
BASE = sys.argv[3]
TIP = sys.argv[4]
TOKEN = os.environ["GH_TOKEN"]
API = "https://api.github.com"


def git(*args, binary=False):
    out = subprocess.run(["git", *args], capture_output=True, check=True).stdout
    return out if binary else out.decode("utf-8")


def call(method, path, payload=None):
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(API + path, data=data, method=method)
    req.add_header("Authorization", "token " + TOKEN)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("User-Agent", "ejee-push-script")
    if data:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode()[:800]
        raise SystemExit("HTTP %s %s %s -> %s" % (e.code, method, path, body))


def iso(epoch, off):
    """git 的 '1792382893 +0800' -> '2026-10-19T11:28:13+08:00'"""
    epoch, off = int(epoch), off.strip()
    sign = -1 if off[0] == "-" else 1
    secs = sign * (int(off[1:3]) * 3600 + int(off[3:5]) * 60)
    t = epoch + secs
    import time
    st = time.gmtime(t)
    return (time.strftime("%Y-%m-%dT%H:%M:%S", st) + off[:3] + ":" + off[3:5])


def ident(line):
    # author EJEE-Pet <1483152117@qq.com> 1792382893 +0800
    left, epoch, off = line.rsplit(" ", 2)
    name, _, rest = left.partition(" <")
    email = rest.rstrip(">")
    return {"name": name, "email": email, "date": iso(epoch, off)}


commits = git("rev-list", "--reverse", "%s..%s" % (BASE, TIP)).split()
print("commits to replay: %d" % len(commits))

tip_sha = BASE
for c in commits:
    raw = git("cat-file", "commit", c)
    head = raw.split("\n\n", 1)[0].splitlines()
    msg = raw.split("\n\n", 1)[1]
    author = committer = None
    for ln in head:
        if ln.startswith("author "):
            author = ident(ln[7:])
        elif ln.startswith("committer "):
            committer = ident(ln[10:])
    tree = git("rev-parse", c + "^{tree}").strip()
    parent = git("rev-parse", c + "^").strip()
    assert parent == tip_sha, "history mismatch: %s parent %s != %s" % (c, parent, tip_sha)

    # 逐个文件替换到父 tree 上
    changed = git("diff-tree", "-r", "--no-commit-id", "--name-only", c + "^", c).split()
    entries = []
    for path in changed:
        res = git("ls-tree", c, "--", path).strip()
        if not res:                        # 删除
            entries.append({"path": path, "mode": "100644", "type": "blob", "sha": None})
            continue
        meta, _, _ = res.partition("\t")
        mode, typ, sha = meta.split()
        blob = git("cat-file", "blob", "%s:%s" % (c, path), binary=True)
        up = call("POST", "/repos/%s/git/blobs" % REPO, {
            "content": base64.b64encode(blob).decode(), "encoding": "base64"})
        entries.append({"path": path, "mode": mode, "type": typ, "sha": up["sha"]})

    parent_tree = git("rev-parse", tip_sha + "^{tree}").strip()
    nt = call("POST", "/repos/%s/git/trees" % REPO,
              {"base_tree": parent_tree, "tree": entries})
    if nt["sha"] != tree:
        print("  ! tree sha differs: %s vs local %s" % (nt["sha"], tree))

    nc = call("POST", "/repos/%s/git/commits" % REPO, {
        "message": msg, "tree": nt["sha"], "parents": [tip_sha],
        "author": author, "committer": committer})
    mark = "OK " if nc["sha"] == c else "SHA-DIFF"
    print("  %s %s -> %s  %s" % (mark, c[:8], nc["sha"][:8],
                                 msg.splitlines()[0][:60]))
    tip_sha = nc["sha"]

call("PATCH", "/repos/%s/git/refs/heads/%s" % (REPO, BRANCH),
     {"sha": tip_sha, "force": False})
final = call("GET", "/repos/%s/git/ref/heads/%s" % (REPO, BRANCH))
print("remote %s now at %s" % (BRANCH, final["object"]["sha"]))
print("local HEAD         %s" % git("rev-parse", "HEAD").strip())
