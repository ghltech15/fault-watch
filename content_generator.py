"""
Content Generator Module for fault.watch
Generates TikTok-ready 9:16 graphics from dashboard data.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional, Dict, Any

from PIL import Image, ImageDraw, ImageFont


class TemplateType(Enum):
    """Content template types for different market events."""
    PRICE_ALERT = "price_alert"
    COUNTDOWN = "countdown"
    BANK_CRISIS = "bank_crisis"
    DAILY_SUMMARY = "daily_summary"


@dataclass
class ContentConfig:
    """Configuration for content generation."""
    output_dir: Path = field(default_factory=lambda: Path("./content-output"))
    image_width: int = 1080  # TikTok 9:16
    image_height: int = 1920
    brand_color: str = "#e31837"  # CNN red
    background_color: str = "#0d0d0d"
    text_color: str = "#ffffff"
    secondary_color: str = "#888888"
    font_path: Optional[str] = None  # Use default


@dataclass
class VideoConfig:
    """Configuration for video generation."""
    duration: int = 10  # seconds
    fps: int = 30
    include_audio: bool = True
    audio_file: Optional[str] = "assets/audio/dramatic_bg.mp3"


class ContentGenerator:
    """
    Generates branded 9:16 content from market data.

    Supports static images and video (video implemented in 02-02).
    """

    def __init__(self, config: ContentConfig = None):
        self.config = config or ContentConfig()
        self._ensure_dirs()

    def _ensure_dirs(self) -> None:
        """Create output directories if they don't exist."""
        images_dir = self.config.output_dir / "images"
        videos_dir = self.config.output_dir / "videos"
        images_dir.mkdir(parents=True, exist_ok=True)
        videos_dir.mkdir(parents=True, exist_ok=True)

    def _get_timestamp(self) -> str:
        """Get formatted timestamp for filenames."""
        return datetime.now().strftime("%Y%m%d_%H%M%S")

    def _hex_to_rgb(self, hex_color: str) -> tuple:
        """Convert hex color to RGB tuple."""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def _create_base_canvas(self) -> Image.Image:
        """
        Create base canvas with branded styling.

        Returns:
            1080x1920 image with dark background and brand gradient.
        """
        # Create dark background
        bg_color = self._hex_to_rgb(self.config.background_color)
        canvas = Image.new('RGB', (self.config.image_width, self.config.image_height), bg_color)
        draw = ImageDraw.Draw(canvas)

        # Add top gradient fade (brand color at 20% opacity effect)
        brand_rgb = self._hex_to_rgb(self.config.brand_color)
        gradient_height = 200
        for y in range(gradient_height):
            # Fade from brand color to background
            alpha = 1 - (y / gradient_height)
            r = int(bg_color[0] + (brand_rgb[0] - bg_color[0]) * alpha * 0.2)
            g = int(bg_color[1] + (brand_rgb[1] - bg_color[1]) * alpha * 0.2)
            b = int(bg_color[2] + (brand_rgb[2] - bg_color[2]) * alpha * 0.2)
            draw.line([(0, y), (self.config.image_width, y)], fill=(r, g, b))

        # Add watermark at bottom
        try:
            font = ImageFont.truetype("arial.ttf", 24)
        except OSError:
            font = ImageFont.load_default()

        watermark = "fault.watch"
        bbox = draw.textbbox((0, 0), watermark, font=font)
        text_width = bbox[2] - bbox[0]
        x = (self.config.image_width - text_width) // 2
        y = self.config.image_height - 60
        draw.text((x, y), watermark, fill=self._hex_to_rgb(self.config.secondary_color), font=font)

        return canvas

    def generate_image(self, data: Dict[str, Any], template: TemplateType) -> Path:
        """
        Generate a branded 9:16 image from data.

        Args:
            data: Dictionary with template-specific data
            template: TemplateType enum value

        Returns:
            Path to generated image file
        """
        canvas = self._create_base_canvas()
        draw = ImageDraw.Draw(canvas)

        # Route to template-specific drawing
        if template == TemplateType.PRICE_ALERT:
            self._draw_price_alert(canvas, draw, data)
        elif template == TemplateType.COUNTDOWN:
            self._draw_countdown(canvas, draw, data)
        elif template == TemplateType.BANK_CRISIS:
            self._draw_bank_crisis(canvas, draw, data)
        elif template == TemplateType.DAILY_SUMMARY:
            self._draw_daily_summary(canvas, draw, data)

        # Save to output
        filename = f"{template.value}_{self._get_timestamp()}.png"
        output_path = self.config.output_dir / "images" / filename
        canvas.save(output_path, "PNG")

        return output_path

    def _draw_price_alert(self, canvas: Image.Image, draw: ImageDraw.Draw, data: Dict[str, Any]) -> None:
        """Draw price alert template."""
        # Will be implemented in Task 3
        pass

    def _draw_countdown(self, canvas: Image.Image, draw: ImageDraw.Draw, data: Dict[str, Any]) -> None:
        """Draw countdown template."""
        # Will be implemented in Task 3
        pass

    def _draw_bank_crisis(self, canvas: Image.Image, draw: ImageDraw.Draw, data: Dict[str, Any]) -> None:
        """Draw bank crisis template."""
        # Will be implemented in Task 3
        pass

    def _draw_daily_summary(self, canvas: Image.Image, draw: ImageDraw.Draw, data: Dict[str, Any]) -> None:
        """Draw daily summary template."""
        # Will be implemented in Task 3
        pass

    def generate_video(self, data: Dict[str, Any], template: TemplateType, config: VideoConfig = None) -> Path:
        """
        Generate a TikTok-ready video from data.

        NOTE: Implemented in Phase 02-02.

        Args:
            data: Dictionary with template-specific data
            template: TemplateType enum value
            config: VideoConfig for duration, fps, audio settings

        Returns:
            Path to generated video file

        Raises:
            NotImplementedError: Until Phase 02-02 is complete
        """
        raise NotImplementedError("Video generation will be implemented in Phase 02-02")
