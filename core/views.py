from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotFound, JsonResponse
from django.contrib import messages
import base64
from urllib.parse import urlparse
import urllib.request
import urllib.error

from .forms import FeatForm
from .models import Feat, Spell, Item, Language, Skill


@login_required
def home(request):
    return render(request, "home.html", {"title": "Dashboard"})


@login_required
def feat_create(request):
    if request.method == "POST":
        form = FeatForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Feature created.")
            return redirect("core:home")
    else:
        form = FeatForm()
    return render(request, "feat_form.html", {"form": form, "title": "Create Feature"})


@login_required
def creation_search(request):
    q = request.GET.get("q", "")
    results = []
    if q:
        lookups = [
            ("feat", Feat.objects.filter(name__icontains=q)[:5]),
            ("spell", Spell.objects.filter(name__icontains=q)[:5]),
            ("item", Item.objects.filter(name__icontains=q)[:5]),
            ("language", Language.objects.filter(name__icontains=q)[:5]),
            ("skill", Skill.objects.filter(name__icontains=q)[:5]),
        ]
        for model_name, qs in lookups:
            for obj in qs:
                results.append({"model": model_name, "id": obj.id, "name": obj.name})
    return JsonResponse({"results": results})


def _transform_github_base(url: str) -> str:
    """Convert common GitHub folder URLs into raw file URLs.

    Accepts formats like:
      https://github.com/user/repo/tree/branch/path/to/theme
    and returns:
      https://raw.githubusercontent.com/user/repo/branch/path/to/theme
    Other hosts are returned unchanged.
    """
    try:
        p = urlparse(url)
        if p.netloc == "github.com":
            parts = [seg for seg in p.path.strip("/").split("/") if seg]
            # user/repo/tree/branch/optional/path
            if len(parts) >= 4 and parts[2] == "tree":
                user, repo, _tree, branch = parts[:4]
                rest = "/".join(parts[4:])
                base = f"https://raw.githubusercontent.com/{user}/{repo}/{branch}"
                return base + (f"/{rest}" if rest else "")
        return url
    except Exception:
        return url


def dice_theme_proxy(request, base_b64: str, res_path: str):
    """Proxy DiceBox theme assets, rewriting GitHub URLs to raw content and
    serving with correct content-type for DiceBox.

    Route: /dice-theme/<base_b64>/<res_path>
    Where base_b64 is a URL-safe base64 of the theme base URL (folder containing theme.config.json).
    """
    # Decode base64 urlsafe without padding
    padded = base_b64 + "=" * ((4 - len(base_b64) % 4) % 4)
    try:
        base_url = base64.urlsafe_b64decode(padded.encode()).decode()
    except Exception:
        return HttpResponseBadRequest("Invalid base URL")

    base_url = _transform_github_base(base_url)
    # Allow only http(s)
    parsed = urlparse(base_url)
    if parsed.scheme not in ("http", "https"):
        return HttpResponseBadRequest("Unsupported scheme")

    # Construct remote URL, but serve from local cache if present
    safe_res = "/".join([p for p in res_path.split('/') if p not in ("..", "")])
    from django.conf import settings
    cache_root = settings.MEDIA_ROOT / "dice_theme_cache" / base_b64
    local_path = cache_root / safe_res
    if local_path.exists() and local_path.is_file():
        ext = safe_res.rsplit(".", 1)[-1].lower() if "." in safe_res else ""
        ct_map = {
            "json": "application/json",
            "png": "image/png",
            "jpg": "image/jpeg",
            "jpeg": "image/jpeg",
            "webp": "image/webp",
            "wasm": "application/wasm",
            "js": "application/javascript",
            "gif": "image/gif",
            "svg": "image/svg+xml",
        }
        content_type = ct_map.get(ext, "application/octet-stream")
        with open(local_path, "rb") as fh:
            data = fh.read()
        resp = HttpResponse(data, content_type=content_type)
        resp["Cache-Control"] = "public, max-age=604800"
        resp["Access-Control-Allow-Origin"] = "*"
        return resp

    remote = base_url.rstrip("/") + "/" + safe_res.lstrip("/")

    req = urllib.request.Request(
        remote,
        headers={
            "User-Agent": "better5e-dice-proxy/1.0",
            "Accept": "application/json, image/*, */*",
            "Cache-Control": "no-cache",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            content = resp.read()
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return HttpResponseNotFound("Not found")
        return HttpResponse(f"Upstream error {e.code}", status=502)
    except Exception:
        return HttpResponse("Upstream fetch failed", status=502)

    # Map content-type by extension
    ext = res_path.rsplit(".", 1)[-1].lower() if "." in res_path else ""
    ct_map = {
        "json": "application/json",
        "png": "image/png",
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "webp": "image/webp",
        "wasm": "application/wasm",
        "js": "application/javascript",
        "gif": "image/gif",
        "svg": "image/svg+xml",
    }
    content_type = ct_map.get(ext, "application/octet-stream")

    resp = HttpResponse(content, content_type=content_type)
    resp["Cache-Control"] = "public, max-age=3600"
    resp["Access-Control-Allow-Origin"] = "*"
    return resp


@login_required
def dice_theme_test(request):
    url = request.POST.get("url") or request.GET.get("url")
    if not url and request.body:
        try:
            import json
            payload = json.loads(request.body.decode("utf-8"))
            url = payload.get("url")
        except Exception:
            url = None
    if not url:
        return JsonResponse({"ok": False, "error": "Missing url"}, status=400)
    base_url = _transform_github_base(url)
    config_url = base_url.rstrip("/") + "/theme.config.json"
    req = urllib.request.Request(config_url, headers={"User-Agent": "better5e-dice-proxy/1.0", "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            raw = resp.read()
    except Exception as e:
        return JsonResponse({"ok": False, "error": f"Fetch failed: {e}"}, status=502)
    import json
    try:
        data = json.loads(raw.decode("utf-8"))
    except Exception:
        return JsonResponse({"ok": False, "error": "Invalid JSON in theme.config.json"}, status=400)
    if "diceAvailable" not in data:
        return JsonResponse({"ok": False, "error": "Missing diceAvailable in theme.config.json"}, status=400)
    mesh = data.get("meshFile", "default.json")
    # Return a small list of expected assets
    assets = ["theme.config.json", mesh]
    mat = data.get("material", {})
    def add_tex(v):
        if isinstance(v, str) and v:
            assets.append(v)
        elif isinstance(v, dict):
            for val in v.values():
                if isinstance(val, str) and val:
                    assets.append(val)
    add_tex(mat.get("diffuseTexture"))
    add_tex(mat.get("bumpTexture"))
    add_tex(mat.get("specularTexture"))
    mat = data.get("material", {})
    material_type = mat.get("type") if isinstance(mat, dict) else None
    theme_color = data.get("themeColor")
    return JsonResponse({
        "ok": True,
        "message": "Theme config looks valid.",
        "meshFile": mesh,
        "assets": assets,
        "materialType": material_type,
        "themeColor": theme_color,
        "config": data,
    })


@login_required
def dice_theme_load(request):
    url = request.POST.get("url") or request.GET.get("url")
    if not url and request.body:
        try:
            import json
            payload = json.loads(request.body.decode("utf-8"))
            url = payload.get("url")
        except Exception:
            url = None
    if not url:
        return JsonResponse({"ok": False, "error": "Missing url"}, status=400)
    base_url = _transform_github_base(url)
    import json
    def fetch(path):
        req = urllib.request.Request(path, headers={"User-Agent": "better5e-dice-proxy/1.0", "Accept": "*/*"})
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.read()
    try:
        cfg_bytes = fetch(base_url.rstrip("/") + "/theme.config.json")
        cfg = json.loads(cfg_bytes.decode("utf-8"))
    except Exception as e:
        return JsonResponse({"ok": False, "error": f"Failed to load theme.config.json: {e}"}, status=502)
    files = ["theme.config.json"]
    mesh_file = cfg.get("meshFile", "default.json")
    files.append(mesh_file)
    mat = cfg.get("material", {})
    def add_tex(v):
        if isinstance(v, str) and v:
            files.append(v)
        elif isinstance(v, dict):
            for val in v.values():
                if isinstance(val, str) and val:
                    files.append(val)
    add_tex(mat.get("diffuseTexture"))
    add_tex(mat.get("bumpTexture"))
    add_tex(mat.get("specularTexture"))
    # Save to local cache folder keyed by base_b64
    from django.conf import settings
    base_b64 = base64.urlsafe_b64encode(base_url.encode()).decode().rstrip("=").replace("+", "-").replace("/", "_")
    cache_root = settings.MEDIA_ROOT / "dice_theme_cache" / base_b64
    cache_root.mkdir(parents=True, exist_ok=True)
    saved = []
    for rel in files:
        rel_safe = "/".join([p for p in rel.split('/') if p not in ("..", "")])
        remote = base_url.rstrip("/") + "/" + rel_safe
        try:
            data = fetch(remote)
        except Exception as e:
            return JsonResponse({"ok": False, "error": f"Failed to fetch {rel}: {e}"}, status=502)
        dest = cache_root / rel_safe
        dest.parent.mkdir(parents=True, exist_ok=True)
        with open(dest, "wb") as f:
            f.write(data)
        saved.append(rel_safe)
    return JsonResponse({"ok": True, "message": "Theme cached locally.", "base_b64": base_b64, "saved": saved})
