from django.utils.text import slugify


def slugify_name(model, validated_data):
    base_slug = slugify(validated_data["name"])
    slug = base_slug
    counter = 1
    while model.objects.filter(slug=slug).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1
    validated_data["slug"] = slug
    return validated_data
