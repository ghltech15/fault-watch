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

    def _get_font(self, size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
        """Get a font at specified size, with fallback to default."""
        font_names = ["arialbd.ttf", "Arial Bold.ttf"] if bold else ["arial.ttf", "Arial.ttf"]
        for font_name in font_names:
            try:
                return ImageFont.truetype(font_name, size)
            except OSError:
                continue
        return ImageFont.load_default()

    def _center_text(self, draw: ImageDraw.Draw, text: str, y: int, font: ImageFont.FreeTypeFont, fill: tuple) -> None:
        """Draw centered text at specified y position."""
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        x = (self.config.image_width - text_width) // 2
        draw.text((x, y), text, fill=fill, font=font)

    def _draw_price_alert(self, canvas: Image.Image, draw: ImageDraw.Draw, data: Dict[str, Any]) -> None:
        """
        Draw price alert template.

        Expected data keys:
            - asset: str (e.g., "SILVER")
            - price: float (e.g., 89.50)
            - change: float (percentage, e.g., 5.2 or -3.1)
        """
        asset = data.get('asset', 'SILVER')
        price = data.get('price', 0.0)
        change = data.get('change', 0.0)

        white = self._hex_to_rgb(self.config.text_color)
        brand = self._hex_to_rgb(self.config.brand_color)
        secondary = self._hex_to_rgb(self.config.secondary_color)

        # "BREAKING" label at top
        font_label = self._get_font(48, bold=True)
        self._center_text(draw, "BREAKING", 280, font_label, brand)

        # Asset name (large)
        font_asset = self._get_font(120, bold=True)
        self._center_text(draw, asset.upper(), 380, font_asset, white)

        # Huge price in center
        font_price = self._get_font(200, bold=True)
        price_text = f"${price:.2f}"
        self._center_text(draw, price_text, 600, font_price, white)

        # Change percentage with arrow
        arrow = "▲" if change >= 0 else "▼"
        change_color = (0, 200, 0) if change >= 0 else brand  # Green for up, red for down
        font_change = self._get_font(80, bold=True)
        change_text = f"{arrow} {abs(change):.1f}%"
        self._center_text(draw, change_text, 850, font_change, change_color)

        # Timestamp at bottom
        font_time = self._get_font(36)
        timestamp = datetime.now().strftime("%B %d, %Y • %I:%M %p")
        self._center_text(draw, timestamp, 1750, font_time, secondary)

    def _draw_countdown(self, canvas: Image.Image, draw: ImageDraw.Draw, data: Dict[str, Any]) -> None:
        """
        Draw countdown template.

        Expected data keys:
            - days: int (days remaining)
            - event: str (event name, e.g., "COMEX Deadline")
            - date: str (target date, e.g., "March 27, 2026")
        """
        days = data.get('days', 0)
        event = data.get('event', 'DEADLINE')
        date = data.get('date', '')

        white = self._hex_to_rgb(self.config.text_color)
        brand = self._hex_to_rgb(self.config.brand_color)
        secondary = self._hex_to_rgb(self.config.secondary_color)

        # "DEADLINE" label at top
        font_label = self._get_font(60, bold=True)
        self._center_text(draw, "DEADLINE", 300, font_label, brand)

        # Giant days number in center
        font_days = self._get_font(350, bold=True)
        days_text = str(days)
        self._center_text(draw, days_text, 500, font_days, white)

        # "DAYS REMAINING" below number
        font_subtitle = self._get_font(60, bold=True)
        self._center_text(draw, "DAYS REMAINING", 900, font_subtitle, secondary)

        # Event name
        font_event = self._get_font(48)
        self._center_text(draw, event.upper(), 1050, font_event, white)

        # Target date
        font_date = self._get_font(40)
        self._center_text(draw, date, 1150, font_date, secondary)

    def _draw_bank_crisis(self, canvas: Image.Image, draw: ImageDraw.Draw, data: Dict[str, Any]) -> None:
        """
        Draw bank crisis template.

        Expected data keys:
            - bank: str (bank name, e.g., "Morgan Stanley")
            - price: float (stock price)
            - change: float (percentage drop, typically negative)
            - exposure: str (e.g., "$18.5B")
            - loss: str (optional, e.g., "$12.3B")
        """
        bank = data.get('bank', 'BANK')
        price = data.get('price', 0.0)
        change = data.get('change', 0.0)
        exposure = data.get('exposure', '$0')
        loss = data.get('loss', '')

        white = self._hex_to_rgb(self.config.text_color)
        brand = self._hex_to_rgb(self.config.brand_color)
        secondary = self._hex_to_rgb(self.config.secondary_color)

        # Red flash bar at top
        draw.rectangle([(0, 250), (self.config.image_width, 320)], fill=brand)

        # Bank name in white on red bar
        font_bank = self._get_font(60, bold=True)
        self._center_text(draw, bank.upper(), 255, font_bank, white)

        # "CRISIS" label
        font_crisis = self._get_font(100, bold=True)
        self._center_text(draw, "CRISIS", 400, font_crisis, brand)

        # Stock price
        font_price = self._get_font(140, bold=True)
        price_text = f"${price:.2f}"
        self._center_text(draw, price_text, 550, font_price, white)

        # Dramatic percentage drop
        font_change = self._get_font(80, bold=True)
        change_text = f"▼ {abs(change):.1f}%"
        self._center_text(draw, change_text, 720, font_change, brand)

        # Exposure section
        font_label = self._get_font(36)
        font_value = self._get_font(60, bold=True)

        self._center_text(draw, "SILVER EXPOSURE", 900, font_label, secondary)
        self._center_text(draw, exposure, 950, font_value, white)

        # Loss if provided
        if loss:
            self._center_text(draw, "POTENTIAL LOSS", 1100, font_label, secondary)
            self._center_text(draw, loss, 1150, font_value, brand)

    def _draw_daily_summary(self, canvas: Image.Image, draw: ImageDraw.Draw, data: Dict[str, Any]) -> None:
        """
        Draw daily summary template.

        Expected data keys:
            - silver: float (silver price)
            - gold: float (gold price)
            - ms: float (Morgan Stanley price)
            - vix: float (VIX level)
            - risk: float (risk index 0-10)
            - date: str (optional, defaults to today)
        """
        silver = data.get('silver', 0.0)
        gold = data.get('gold', 0.0)
        ms = data.get('ms', 0.0)
        vix = data.get('vix', 0.0)
        risk = data.get('risk', 0.0)
        date_str = data.get('date', datetime.now().strftime("%B %d, %Y"))

        white = self._hex_to_rgb(self.config.text_color)
        brand = self._hex_to_rgb(self.config.brand_color)
        secondary = self._hex_to_rgb(self.config.secondary_color)

        # "DAILY RECAP" header
        font_header = self._get_font(70, bold=True)
        self._center_text(draw, "DAILY RECAP", 280, font_header, white)

        # Date below header
        font_date = self._get_font(36)
        self._center_text(draw, date_str, 370, font_date, secondary)

        # Metrics list
        font_label = self._get_font(40)
        font_value = self._get_font(70, bold=True)

        metrics = [
            ("SILVER", f"${silver:.2f}"),
            ("GOLD", f"${gold:.2f}"),
            ("MORGAN STANLEY", f"${ms:.2f}"),
            ("VIX", f"{vix:.1f}"),
        ]

        y_start = 500
        y_spacing = 180

        for i, (label, value) in enumerate(metrics):
            y = y_start + (i * y_spacing)
            self._center_text(draw, label, y, font_label, secondary)
            self._center_text(draw, value, y + 50, font_value, white)

        # Risk index section
        risk_y = y_start + (len(metrics) * y_spacing) + 50

        # Risk color: green < 4, yellow 4-7, red > 7
        if risk < 4:
            risk_color = (0, 200, 0)
        elif risk < 7:
            risk_color = (255, 200, 0)
        else:
            risk_color = brand

        self._center_text(draw, "RISK INDEX", risk_y, font_label, secondary)
        font_risk = self._get_font(100, bold=True)
        self._center_text(draw, f"{risk:.1f}", risk_y + 60, font_risk, risk_color)

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
