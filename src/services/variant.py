"""Biến thể nội dung — tránh FB flag duplicate khi đăng cùng caption lên nhiều page."""
import random

EMOJI_PREFIX = ["✨", "🌟", "💕", "🔥", "💫", "💖", "🌸", "👀", "🎀", "🌺"]
EMOJI_SUFFIX = ["✨", "💕", "🥰", "😍", "🌟", "💯", "👌", "🎉", "💖", "🤩"]

OPENING_LINES = [
    "Chị em ơi,",
    "Mom nào đang tìm sản phẩm này không nè,",
    "Hôm nay mình chia sẻ nhanh,",
    "Ai cần cái này thì xem qua nha,",
    "Mình đang xài và thấy ổn lắm nè,",
]

CLOSING_LINES = [
    "Link ở comment nha cả nhà.",
    "Ai cần inbox mình tư vấn thêm.",
    "Mình để link bên dưới comment nhé.",
    "Cần info thêm comment cho mình biết nha.",
    "Mua tại link mình để dưới comment nha.",
]

HASHTAG_SETS = [
    ["#review", "#shopee", "#deal"],
    ["#muasamthongminh", "#santhuong", "#chiemchanh"],
    ["#sale", "#hangtot", "#giare"],
]


def apply_variant(caption: str) -> str:
    prefix = random.choice(EMOJI_PREFIX)
    suffix = random.choice(EMOJI_SUFFIX)
    opening = random.choice(OPENING_LINES)
    closing = random.choice(CLOSING_LINES)
    hashtags = " ".join(random.choice(HASHTAG_SETS))
    return f"{prefix} {opening}\n\n{caption.strip()}\n\n{closing} {suffix}\n{hashtags}"


def build_final_caption(base_caption: str, video_link: str, variant_mode: str) -> str:
    text = apply_variant(base_caption) if variant_mode == "auto_variant" else base_caption
    video_link = (video_link or "").strip()
    if video_link:
        return f"{text}\n\n{video_link}"
    return text
