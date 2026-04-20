from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_GET, require_POST
from django.contrib.admin.views.decorators import staff_member_required

from .forms import ReportItemForm
from .models import Item, ClaimRequest


@login_required(login_url="login")
def report_item(request):
    if request.method == "POST":
        form = ReportItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.reported_by = request.user
            item.save()
            return redirect("index")
    else:
        form = ReportItemForm()

    return render(request, "item/report_item.html", {"form": form})


@login_required(login_url="login")
def retrieve_item(request):
    if request.method == "POST":
        item_id = request.POST.get("item_id")
        claim_note = request.POST.get("claim_note", "").strip()
        item = Item.objects.filter(id=item_id, is_public=True, status=Item.Status.FOUND).first()

        if not item:
            messages.error(request, "Item not available for retrieval.")
            return redirect("retrieve_item")

        if not claim_note:
            messages.error(request, "Please add a short note to support your claim.")
            return redirect("retrieve_item")

        existing_claim = ClaimRequest.objects.filter(
            item=item,
            claimed_by=request.user,
            status=ClaimRequest.Status.PENDING,
        ).exists()
        if existing_claim:
            messages.error(request, "You already have a pending claim for this item.")
            return redirect("retrieve_item")

        ClaimRequest.objects.create(
            item=item,
            claimed_by=request.user,
            note=claim_note,
        )
        item.status = Item.Status.CLAIMED
        item.claim_notes = f"Latest claim by {request.user.username}: {claim_note}"
        item.save(update_fields=["status", "claim_notes", "updated_at"])
        messages.success(request, f"Claim request submitted for {item.name}.")
        return redirect("retrieve_item")

    search = request.GET.get("q", "").strip()
    items = Item.objects.filter(is_public=True, status=Item.Status.FOUND).select_related("category", "reported_by")

    if search:
        items = items.filter(Q(name__icontains=search) | Q(location__icontains=search))

    context = {
        "items": items[:30],
        "search": search,
    }
    return render(request, "item/retrieve_item.html", context)


@login_required(login_url="login")
@require_POST
def api_submit_claim(request):
    item_id = request.POST.get("item_id")
    claim_note = request.POST.get("claim_note", "").strip()
    item = Item.objects.filter(id=item_id, is_public=True, status=Item.Status.FOUND).first()

    if not item:
        return JsonResponse({"detail": "Item not available for retrieval."}, status=404)

    if not claim_note:
        return JsonResponse({"detail": "Please provide claim_note."}, status=400)

    existing_claim = ClaimRequest.objects.filter(
        item=item,
        claimed_by=request.user,
        status=ClaimRequest.Status.PENDING,
    ).exists()
    if existing_claim:
        return JsonResponse({"detail": "Pending claim already exists."}, status=400)

    claim = ClaimRequest.objects.create(
        item=item,
        claimed_by=request.user,
        note=claim_note,
    )
    item.status = Item.Status.CLAIMED
    item.claim_notes = f"Latest claim by {request.user.username}: {claim_note}"
    item.save(update_fields=["status", "claim_notes", "updated_at"])

    return JsonResponse(
        {
            "message": "Claim submitted.",
            "claim": {
                "id": claim.id,
                "item_id": claim.item_id,
                "claimed_by": claim.claimed_by.username,
                "status": claim.status,
            },
        },
        status=201,
    )


@staff_member_required(login_url="login")
@require_GET
def api_admin_claims(request):
    claims = ClaimRequest.objects.select_related("item", "claimed_by")[:100]
    data = [
        {
            "id": claim.id,
            "item": claim.item.name,
            "item_id": claim.item_id,
            "claimed_by": claim.claimed_by.username,
            "status": claim.status,
            "note": claim.note,
            "created_at": claim.created_at.isoformat(),
        }
        for claim in claims
    ]
    return JsonResponse({"results": data})
