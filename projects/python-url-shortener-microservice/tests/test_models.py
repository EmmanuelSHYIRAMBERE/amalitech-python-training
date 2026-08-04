"""Tests for shortener models, generators, validators, schemas, and protocols.

Best-practices additions (from labs analysis):
  - __repr__ on Tag, URL, Click, User
  - __eq__ / __hash__ on Tag and URL
  - User.is_valid_tier() @staticmethod
  - ShortenerError exception hierarchy
"""

import string
from datetime import timedelta

import pytest
from django.db.models import Count
from django.utils import timezone

from shortener.generators import BaseShortCodeGenerator, default_generator
from shortener.models import URL, Click, Tag
from shortener.protocols import ShortCodeGenerator
from shortener.schemas import ClickResult, ShortenRequest, ShortenResult
from shortener.validators import validate_short_code, validate_url_scheme
from users.models import User

# ---------------------------------------------------------------------------
# Exception hierarchy
# ---------------------------------------------------------------------------


def test_shortener_error_is_base_exception() -> None:
    from shortener.exceptions import ShortenerError

    assert issubclass(ShortenerError, Exception)


def test_short_link_inactive_error_message() -> None:
    from shortener.exceptions import ShortLinkInactiveError

    exc = ShortLinkInactiveError("aB3xYz")
    assert "aB3xYz" in str(exc)
    assert exc.short_code == "aB3xYz"


def test_short_link_expired_error_message() -> None:
    from shortener.exceptions import ShortLinkExpiredError

    exc = ShortLinkExpiredError("aB3xYz")
    assert "aB3xYz" in str(exc)
    assert exc.short_code == "aB3xYz"


def test_short_code_collision_error_message() -> None:
    from shortener.exceptions import ShortCodeCollisionError

    exc = ShortCodeCollisionError(attempts=5)
    assert "5" in str(exc)
    assert exc.attempts == 5


def test_exception_hierarchy_is_correct() -> None:
    from shortener.exceptions import (
        ShortCodeCollisionError,
        ShortCodeError,
        ShortenerError,
        ShortLinkError,
        ShortLinkExpiredError,
        ShortLinkInactiveError,
    )

    assert issubclass(ShortLinkError, ShortenerError)
    assert issubclass(ShortLinkInactiveError, ShortLinkError)
    assert issubclass(ShortLinkExpiredError, ShortLinkError)
    assert issubclass(ShortCodeError, ShortenerError)
    assert issubclass(ShortCodeCollisionError, ShortCodeError)


# ---------------------------------------------------------------------------
# SecureShortCodeGenerator (unchanged from Mod 5)
# ---------------------------------------------------------------------------


def test_generator_returns_string() -> None:
    assert isinstance(default_generator.generate(), str)


def test_generator_default_length() -> None:
    assert len(default_generator.generate()) == 6


def test_generator_custom_length() -> None:
    assert len(default_generator.generate(length=10)) == 10


def test_generator_only_alphanumeric_chars() -> None:
    allowed = set(string.ascii_letters + string.digits)
    for _ in range(20):
        code = default_generator.generate()
        assert set(code).issubset(allowed), f"Non-alphanumeric chars in: {code!r}"


def test_generator_produces_different_codes_on_successive_calls() -> None:
    codes = {default_generator.generate() for _ in range(10)}
    assert len(codes) == 10


def test_generator_callable_interface() -> None:
    code = default_generator(length=6)
    assert isinstance(code, str)
    assert len(code) == 6


# ---------------------------------------------------------------------------
# Protocol and ABC structural checks (unchanged from Mod 5)
# ---------------------------------------------------------------------------


def test_secure_generator_is_instance_of_abc() -> None:
    assert isinstance(default_generator, BaseShortCodeGenerator)


def test_secure_generator_satisfies_protocol() -> None:
    assert isinstance(default_generator, ShortCodeGenerator)


def test_plain_function_satisfies_protocol() -> None:
    def my_gen(length: int = 6) -> str:
        return "x" * length

    assert isinstance(my_gen, ShortCodeGenerator)


def test_base_generator_cannot_be_instantiated() -> None:
    with pytest.raises(TypeError):
        BaseShortCodeGenerator()  # type: ignore[abstract]


# ---------------------------------------------------------------------------
# Validators (unchanged from Mod 5)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("code", ["abc123", "aB3xYz", "abcd", "abcdefghij"])
def test_validate_short_code_accepts_valid(code: str) -> None:
    assert validate_short_code(code) is True


@pytest.mark.parametrize(
    "code", ["ab", "../admin", "<script>", "abc 123", "abc-123!", ""]
)
def test_validate_short_code_rejects_invalid(code: str) -> None:
    assert validate_short_code(code) is False


@pytest.mark.parametrize("url", ["https://example.com", "http://example.com/path?q=1"])
def test_validate_url_scheme_accepts_http_https(url: str) -> None:
    assert validate_url_scheme(url) is True


@pytest.mark.parametrize("url", ["ftp://example.com", "not-a-url", "", "http://"])
def test_validate_url_scheme_rejects_non_http(url: str) -> None:
    assert validate_url_scheme(url) is False


# ---------------------------------------------------------------------------
# Dataclasses / schemas (Mod 5 + Mod 6 ClickResult)
# ---------------------------------------------------------------------------


def test_shorten_request_stores_url() -> None:
    req = ShortenRequest(original_url="https://example.com")
    assert req.original_url == "https://example.com"


def test_shorten_request_post_init_rejects_empty_url() -> None:
    """__post_init__ must raise ValueError for empty original_url."""
    with pytest.raises(ValueError, match="non-empty"):
        ShortenRequest(original_url="")


def test_shorten_request_post_init_rejects_whitespace_url() -> None:
    with pytest.raises(ValueError, match="non-empty"):
        ShortenRequest(original_url="   ")


def test_shorten_result_is_frozen() -> None:
    """ShortenResult must be immutable (frozen=True)."""
    from dataclasses import FrozenInstanceError

    result = ShortenResult(
        short_code="abc123",
        original_url="https://example.com",
        short_url="http://localhost/abc123/",
        created_at="2025-01-01T00:00:00Z",
    )
    with pytest.raises(FrozenInstanceError):
        result.short_code = "other"  # type: ignore[misc]


def test_shorten_result_stores_all_fields() -> None:
    result = ShortenResult(
        short_code="abc123",
        original_url="https://example.com",
        short_url="http://localhost/abc123/",
        created_at="2025-01-01T00:00:00Z",
    )
    assert result.short_code == "abc123"
    assert result.short_url == "http://localhost/abc123/"


def test_shorten_result_as_dict() -> None:
    """as_dict() must return all four fields as a plain dict."""
    result = ShortenResult(
        short_code="abc123",
        original_url="https://example.com",
        short_url="http://localhost/abc123/",
        created_at="2025-01-01T00:00:00Z",
    )
    d = result.as_dict()
    assert d["short_code"] == "abc123"
    assert set(d.keys()) == {"short_code", "original_url", "short_url", "created_at"}


def test_shorten_request_repr_contains_url() -> None:
    req = ShortenRequest(original_url="https://example.com")
    assert "https://example.com" in repr(req)


def test_click_result_stores_required_fields() -> None:
    cr = ClickResult(url_id=1, ip_address="1.2.3.4", user_agent="Mozilla/5.0")
    assert cr.url_id == 1
    assert cr.ip_address == "1.2.3.4"
    assert cr.country is None


def test_click_result_stores_optional_fields() -> None:
    cr = ClickResult(
        url_id=1,
        ip_address="1.2.3.4",
        user_agent="Mozilla/5.0",
        country="RW",
        city="Kigali",
        referrer="https://google.com",
    )
    assert cr.country == "RW"
    assert cr.city == "Kigali"
    assert cr.referrer == "https://google.com"


def test_click_result_is_frozen() -> None:
    """ClickResult must be immutable (frozen=True)."""
    from dataclasses import FrozenInstanceError

    cr = ClickResult(url_id=1, ip_address="1.2.3.4", user_agent="ua")
    with pytest.raises(FrozenInstanceError):
        cr.country = "RW"  # type: ignore[misc]


def test_click_result_has_geo_true_when_both_set() -> None:
    cr = ClickResult(
        url_id=1, ip_address="1.2.3.4", user_agent="ua", country="RW", city="Kigali"
    )
    assert cr.has_geo() is True


def test_click_result_has_geo_false_when_city_missing() -> None:
    cr = ClickResult(url_id=1, ip_address="1.2.3.4", user_agent="ua", country="RW")
    assert cr.has_geo() is False


def test_click_result_has_geo_false_when_both_missing() -> None:
    cr = ClickResult(url_id=1, ip_address="1.2.3.4", user_agent="ua")
    assert cr.has_geo() is False


def test_click_result_is_known_referrer_true() -> None:
    cr = ClickResult(
        url_id=1, ip_address="1.2.3.4", user_agent="ua", referrer="https://google.com"
    )
    assert cr.is_known_referrer() is True


def test_click_result_is_known_referrer_false_when_none() -> None:
    cr = ClickResult(url_id=1, ip_address="1.2.3.4", user_agent="ua")
    assert cr.is_known_referrer() is False


# ---------------------------------------------------------------------------
# User model (Mod 6)
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_user_default_tier_is_free(user: User) -> None:
    assert user.tier == User.Tier.FREE


@pytest.mark.django_db
def test_user_default_is_premium_false(user: User) -> None:
    assert user.is_premium is False


@pytest.mark.django_db
def test_premium_user_tier_and_flag(premium_user: User) -> None:
    assert premium_user.tier == User.Tier.PREMIUM
    assert premium_user.is_premium is True


@pytest.mark.django_db
def test_user_email_is_unique(user: User) -> None:
    from django.db import IntegrityError

    with pytest.raises(IntegrityError):
        User.objects.create_user(
            username="other",
            email=user.email,  # duplicate email
            password="pass",
        )


@pytest.mark.django_db
def test_user_str_contains_username_and_tier(user: User) -> None:
    assert user.username in str(user)
    assert user.tier in str(user)


@pytest.mark.django_db
def test_user_repr_contains_username(user: User) -> None:
    assert user.username in repr(user)
    assert "User" in repr(user)


def test_user_is_valid_tier_accepts_valid() -> None:
    assert User.is_valid_tier("Free") is True
    assert User.is_valid_tier("Premium") is True
    assert User.is_valid_tier("Admin") is True


def test_user_is_valid_tier_rejects_invalid() -> None:
    assert User.is_valid_tier("Unknown") is False
    assert User.is_valid_tier("") is False
    assert User.is_valid_tier("free") is False  # case-sensitive


# ---------------------------------------------------------------------------
# Tag model (Mod 6)
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_tag_str_is_name(tag_marketing: Tag) -> None:
    assert str(tag_marketing) == "Marketing"


@pytest.mark.django_db
def test_tag_repr_contains_name(tag_marketing: Tag) -> None:
    assert "Marketing" in repr(tag_marketing)
    assert "Tag" in repr(tag_marketing)


@pytest.mark.django_db
def test_tag_eq_by_name(db: None) -> None:
    t1, _ = Tag.objects.get_or_create(name="Tech")
    t2, _ = Tag.objects.get_or_create(name="Tech")
    assert t1 == t2


def test_tag_eq_unsaved_instances() -> None:
    """__eq__ works on unsaved Tag instances — safe in tests before DB flush."""
    t1 = Tag(name="Alpha")
    t2 = Tag(name="Alpha")
    assert t1 == t2


def test_tag_neq_different_names() -> None:
    assert Tag(name="A") != Tag(name="B")


def test_tag_hash_consistent_with_eq() -> None:
    t1 = Tag(name="X")
    t2 = Tag(name="X")
    assert hash(t1) == hash(t2)
    assert len({t1, t2}) == 1  # set deduplication works


@pytest.mark.django_db
def test_tag_name_is_unique(tag_marketing: Tag) -> None:
    from django.db import IntegrityError

    with pytest.raises(IntegrityError):
        Tag.objects.create(name="Marketing")


@pytest.mark.django_db
def test_tags_ordered_alphabetically(db: None) -> None:
    Tag.objects.get_or_create(name="Zebra")
    Tag.objects.get_or_create(name="Alpha")
    names = list(Tag.objects.values_list("name", flat=True))
    assert names == sorted(names)


# ---------------------------------------------------------------------------
# URL model — Mod 5 fields (unchanged)
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_url_str_format(created_url: URL) -> None:
    assert str(created_url) == f"{created_url.short_code} → {created_url.original_url}"


@pytest.mark.django_db
def test_url_repr_contains_short_code(created_url: URL) -> None:
    assert created_url.short_code in repr(created_url)
    assert "URL" in repr(created_url)


@pytest.mark.django_db
def test_url_eq_by_pk(created_url: URL, user: User) -> None:
    same = URL.objects.get(pk=created_url.pk)
    assert created_url == same


def test_url_eq_unsaved_by_short_code() -> None:
    u1 = URL(short_code="abc123", original_url="https://a.com")
    u2 = URL(short_code="abc123", original_url="https://b.com")
    assert u1 == u2


def test_url_neq_different_short_codes() -> None:
    assert URL(short_code="aaa111") != URL(short_code="bbb222")


@pytest.mark.django_db
def test_url_created_at_is_set_on_save(created_url: URL) -> None:
    assert created_url.created_at is not None


@pytest.mark.django_db
def test_url_updated_at_is_set_on_save(created_url: URL) -> None:
    assert created_url.updated_at is not None


@pytest.mark.django_db
def test_url_short_code_is_unique(user: User) -> None:
    from django.db import IntegrityError

    URL.objects.create(
        original_url="https://first.com", short_code="unique1", owner=user
    )
    with pytest.raises(IntegrityError):
        URL.objects.create(
            original_url="https://second.com", short_code="unique1", owner=user
        )


@pytest.mark.django_db
def test_url_ordering_is_newest_first(user: User) -> None:
    URL.objects.create(
        original_url="https://first.com", short_code="first1", owner=user
    )
    URL.objects.create(
        original_url="https://second.com", short_code="secnd1", owner=user
    )
    urls = list(URL.objects.all())
    assert urls[0].short_code == "secnd1"
    assert urls[1].short_code == "first1"


# ---------------------------------------------------------------------------
# URL model — Mod 6 new fields
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_url_default_is_active(created_url: URL) -> None:
    assert created_url.is_active is True


@pytest.mark.django_db
def test_url_default_click_count_is_zero(created_url: URL) -> None:
    assert created_url.click_count == 0


@pytest.mark.django_db
def test_url_owner_is_set(created_url: URL, user: User) -> None:
    assert created_url.owner == user


@pytest.mark.django_db
def test_url_is_expired_false_when_no_expiry(created_url: URL) -> None:
    assert created_url.is_expired is False


@pytest.mark.django_db
def test_url_is_expired_false_when_future_expiry(user: User) -> None:
    url = URL.objects.create(
        original_url="https://example.com",
        short_code="futexp",
        owner=user,
        expires_at=timezone.now() + timedelta(days=1),
    )
    assert url.is_expired is False


@pytest.mark.django_db
def test_url_is_expired_true_when_past_expiry(user: User) -> None:
    url = URL.objects.create(
        original_url="https://example.com",
        short_code="pastexp",
        owner=user,
        expires_at=timezone.now() - timedelta(seconds=1),
    )
    assert url.is_expired is True


@pytest.mark.django_db
def test_url_increment_click_count(created_url: URL) -> None:
    created_url.increment_click_count()
    created_url.refresh_from_db()
    assert created_url.click_count == 1


@pytest.mark.django_db
def test_url_increment_click_count_is_atomic(created_url: URL) -> None:
    """Two increments must result in click_count == 2."""
    created_url.increment_click_count()
    created_url.increment_click_count()
    created_url.refresh_from_db()
    assert created_url.click_count == 2


@pytest.mark.django_db
def test_url_tags_can_be_attached(
    created_url: URL, tag_marketing: Tag, tag_social: Tag
) -> None:
    created_url.tags.set([tag_marketing, tag_social])
    assert created_url.tags.count() == 2


@pytest.mark.django_db
def test_url_custom_alias_is_unique(user: User) -> None:
    from django.db import IntegrityError

    URL.objects.create(
        original_url="https://a.com",
        short_code="alias1",
        owner=user,
        custom_alias="myshop",
    )
    with pytest.raises(IntegrityError):
        URL.objects.create(
            original_url="https://b.com",
            short_code="alias2",
            owner=user,
            custom_alias="myshop",
        )


# ---------------------------------------------------------------------------
# Click model (Mod 6)
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_click_is_created(created_url: URL) -> None:
    click = Click.objects.create(
        url=created_url,
        ip_address="1.2.3.4",
        user_agent="Mozilla/5.0",
    )
    assert click.pk is not None
    assert click.clicked_at is not None


@pytest.mark.django_db
def test_click_str_contains_short_code(created_url: URL) -> None:
    click = Click.objects.create(
        url=created_url, ip_address="1.2.3.4", user_agent="Mozilla/5.0"
    )
    assert created_url.short_code in str(click)


@pytest.mark.django_db
def test_click_repr_contains_ip(created_url: URL) -> None:
    click = Click.objects.create(url=created_url, ip_address="9.9.9.9", user_agent="ua")
    assert "9.9.9.9" in repr(click)
    assert "Click" in repr(click)


@pytest.mark.django_db
def test_click_cascade_delete(created_url: URL) -> None:
    Click.objects.create(url=created_url, ip_address="1.2.3.4", user_agent="ua")
    assert Click.objects.count() == 1
    created_url.delete()
    assert Click.objects.count() == 0


# ---------------------------------------------------------------------------
# URLManager / URLQuerySet (Mod 6)
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_active_urls_excludes_inactive(user: User) -> None:
    URL.objects.create(
        original_url="https://a.com", short_code="actv01", owner=user, is_active=True
    )
    URL.objects.create(
        original_url="https://b.com", short_code="inact1", owner=user, is_active=False
    )
    assert URL.objects.active_urls().count() == 1
    assert URL.objects.active_urls().first().short_code == "actv01"  # type: ignore[union-attr]  # noqa: E501


@pytest.mark.django_db
def test_active_urls_excludes_expired(user: User) -> None:
    URL.objects.create(
        original_url="https://a.com",
        short_code="exprd1",
        owner=user,
        expires_at=timezone.now() - timedelta(seconds=1),
    )
    assert URL.objects.active_urls().count() == 0


@pytest.mark.django_db
def test_active_urls_includes_no_expiry(user: User) -> None:
    URL.objects.create(original_url="https://a.com", short_code="noexp1", owner=user)
    assert URL.objects.active_urls().count() == 1


@pytest.mark.django_db
def test_expired_urls_returns_only_expired(user: User) -> None:
    URL.objects.create(
        original_url="https://a.com",
        short_code="exprd2",
        owner=user,
        expires_at=timezone.now() - timedelta(seconds=1),
    )
    URL.objects.create(original_url="https://b.com", short_code="live01", owner=user)
    assert URL.objects.expired_urls().count() == 1


@pytest.mark.django_db
def test_popular_urls_ordered_by_click_count(user: User) -> None:
    low = URL.objects.create(
        original_url="https://low.com", short_code="low001", owner=user, click_count=5
    )
    high = URL.objects.create(
        original_url="https://high.com",
        short_code="high01",
        owner=user,
        click_count=100,
    )
    results = list(URL.objects.popular_urls(top_n=2))
    assert results[0].pk == high.pk
    assert results[1].pk == low.pk


@pytest.mark.django_db
def test_popular_urls_respects_top_n(user: User) -> None:
    for i in range(5):
        URL.objects.create(
            original_url=f"https://example{i}.com",
            short_code=f"pop{i:03d}",
            owner=user,
            click_count=i,
        )
    assert len(list(URL.objects.popular_urls(top_n=3))) == 3


# ---------------------------------------------------------------------------
# Aggregation — annotate() clicks by country (Mod 6)
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_clicks_by_country_aggregation(created_url: URL) -> None:
    """annotate() must compute click totals per country in the DB."""
    Click.objects.create(
        url=created_url, ip_address="1.1.1.1", user_agent="ua", country="RW"
    )
    Click.objects.create(
        url=created_url, ip_address="2.2.2.2", user_agent="ua", country="RW"
    )
    Click.objects.create(
        url=created_url, ip_address="3.3.3.3", user_agent="ua", country="US"
    )

    stats = (
        created_url.clicks.values("country")
        .annotate(total=Count("id"))
        .order_by("-total")
    )
    result = {row["country"]: row["total"] for row in stats}
    assert result["RW"] == 2
    assert result["US"] == 1


@pytest.mark.django_db
def test_select_related_owner_avoids_extra_query(  # type: ignore[no-untyped-def]
    created_url: URL, django_assert_num_queries
) -> None:
    """select_related('owner') must fetch URL + owner in a single query."""
    with django_assert_num_queries(1):
        url = URL.objects.select_related("owner").get(pk=created_url.pk)
        _ = url.owner.username  # accessing owner must NOT trigger a second query


@pytest.mark.django_db
def test_prefetch_related_tags_avoids_n_plus_1(
    created_url: URL,
    tag_marketing: Tag,
    tag_social: Tag,
    django_assert_num_queries,  # type: ignore[no-untyped-def]
) -> None:
    """prefetch_related('tags') must load all tags in exactly 2 queries."""
    created_url.tags.set([tag_marketing, tag_social])
    with django_assert_num_queries(2):  # 1 for URL, 1 for tags
        url = URL.objects.prefetch_related("tags").get(pk=created_url.pk)
        tag_names = [t.name for t in url.tags.all()]
    assert set(tag_names) == {"Marketing", "Social"}
