"""
Content Generator Module for fault.watch
Generates TikTok-ready 9:16 graphics from dashboard data.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional, Dict, Any, List, Callable
import numpy as np

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
    audio_file: Optional[str] = "assets/audio/dramatic_bg.wav"
    alert_sound: Optional[str] = "assets/audio/alert_tone.wav"
    tick_sound: Optional[str] = "assets/audio/countdown_tick.wav"


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

        Args:
            data: Dictionary with template-specific data
            template: TemplateType enum value
            config: VideoConfig for duration, fps, audio settings

        Returns:
            Path to generated video file
        """
        from moviepy import (
            ImageClip, CompositeVideoClip, AudioFileClip,
            concatenate_audioclips
        )

        config = config or VideoConfig()

        # Route to template-specific video generation
        if template == TemplateType.PRICE_ALERT:
            clips = self._create_price_alert_video(data, config)
        elif template == TemplateType.COUNTDOWN:
            clips = self._create_countdown_video(data, config)
        elif template == TemplateType.BANK_CRISIS:
            clips = self._create_bank_crisis_video(data, config)
        elif template == TemplateType.DAILY_SUMMARY:
            clips = self._create_daily_summary_video(data, config)
        else:
            # Fallback: static image as video
            clips = self._create_static_video(data, template, config)

        # Compose final video
        video = CompositeVideoClip(clips, size=(self.config.image_width, self.config.image_height))
        video = video.with_duration(config.duration)

        # Add audio if enabled
        if config.include_audio and config.audio_file and Path(config.audio_file).exists():
            audio = AudioFileClip(config.audio_file)
            # Loop audio if shorter than video
            if audio.duration < config.duration:
                loops_needed = int(np.ceil(config.duration / audio.duration))
                audio = concatenate_audioclips([audio] * loops_needed)
            audio = audio.subclipped(0, config.duration)
            video = video.with_audio(audio)

        # Export video
        filename = f"{template.value}_{self._get_timestamp()}.mp4"
        output_path = self.config.output_dir / "videos" / filename

        video.write_videofile(
            str(output_path),
            fps=config.fps,
            codec='libx264',
            audio_codec='aac',
            temp_audiofile='temp-audio.m4a',
            remove_temp=True,
            logger=None  # Suppress verbose output
        )

        # Clean up
        video.close()

        return output_path

    def _create_frame_at_time(
        self,
        draw_func: Callable,
        data: Dict[str, Any],
        t: float,
        animations: List[Dict[str, Any]]
    ) -> Image.Image:
        """
        Create a single frame at time t with animations applied.

        Args:
            draw_func: Function to draw the template
            data: Template data
            t: Time in seconds
            animations: List of animation configs

        Returns:
            PIL Image for the frame
        """
        canvas = self._create_base_canvas()
        draw = ImageDraw.Draw(canvas)

        # Apply animations to data based on time
        animated_data = data.copy()
        for anim in animations:
            start = anim.get('start', 0)
            end = anim.get('end', 1)
            key = anim.get('key')
            anim_type = anim.get('type', 'fade_in')

            if start <= t <= end:
                progress = (t - start) / (end - start)

                if anim_type == 'fade_in':
                    animated_data[f'{key}_alpha'] = progress
                elif anim_type == 'count_up':
                    target = data.get(key, 0)
                    animated_data[key] = target * progress
                elif anim_type == 'slide_in':
                    animated_data[f'{key}_offset'] = int((1 - progress) * 100)
            elif t > end:
                animated_data[f'{key}_alpha'] = 1.0
                if anim.get('type') == 'count_up':
                    animated_data[key] = data.get(key, 0)

        draw_func(canvas, draw, animated_data)
        return canvas

    def _create_static_video(
        self,
        data: Dict[str, Any],
        template: TemplateType,
        config: VideoConfig
    ) -> List:
        """Create a simple static image video."""
        from moviepy import ImageClip

        # Generate static image
        image_path = self.generate_image(data, template)
        clip = ImageClip(str(image_path)).with_duration(config.duration)
        return [clip]

    def _create_price_alert_video(self, data: Dict[str, Any], config: VideoConfig) -> List:
        """
        Create animated PRICE_ALERT video.

        Timeline:
        - 0-1s: Flash + "BREAKING" appears
        - 1-3s: Asset name fades in
        - 3-6s: Price counts up
        - 6-8s: Percentage slides in
        - 8-10s: Hold final frame
        """
        from moviepy import ImageClip, concatenate_videoclips

        frames = []
        duration = config.duration
        fps = config.fps

        # Generate frames
        for frame_num in range(int(duration * fps)):
            t = frame_num / fps
            canvas = self._create_base_canvas()
            draw = ImageDraw.Draw(canvas)

            white = self._hex_to_rgb(self.config.text_color)
            brand = self._hex_to_rgb(self.config.brand_color)
            secondary = self._hex_to_rgb(self.config.secondary_color)

            asset = data.get('asset', 'SILVER')
            price = data.get('price', 0.0)
            change = data.get('change', 0.0)

            # Flash effect at start (0-0.5s)
            if t < 0.5:
                flash_alpha = 1 - (t / 0.5)
                flash_color = tuple(int(c * flash_alpha) for c in brand)
                draw.rectangle([(0, 0), (self.config.image_width, self.config.image_height)], fill=flash_color)

            # "BREAKING" label (appears at 0.5s)
            if t >= 0.5:
                font_label = self._get_font(48, bold=True)
                alpha = min(1.0, (t - 0.5) / 0.5)
                color = tuple(int(c * alpha) for c in brand)
                self._center_text(draw, "BREAKING", 280, font_label, color)

            # Asset name (fades in 1-2s)
            if t >= 1:
                font_asset = self._get_font(120, bold=True)
                alpha = min(1.0, (t - 1) / 1)
                color = tuple(int(c * alpha) for c in white)
                self._center_text(draw, asset.upper(), 380, font_asset, color)

            # Price counter (counts up 3-6s)
            if t >= 3:
                font_price = self._get_font(200, bold=True)
                if t < 6:
                    progress = (t - 3) / 3
                    current_price = price * progress
                else:
                    current_price = price
                price_text = f"${current_price:.2f}"
                self._center_text(draw, price_text, 600, font_price, white)

            # Change percentage (slides in 6-8s)
            if t >= 6:
                arrow = "▲" if change >= 0 else "▼"
                change_color = (0, 200, 0) if change >= 0 else brand
                font_change = self._get_font(80, bold=True)
                change_text = f"{arrow} {abs(change):.1f}%"

                if t < 8:
                    progress = (t - 6) / 2
                    offset = int((1 - progress) * 200)
                    # Draw with offset (slide from right)
                    bbox = draw.textbbox((0, 0), change_text, font=font_change)
                    text_width = bbox[2] - bbox[0]
                    x = (self.config.image_width - text_width) // 2 + offset
                    draw.text((x, 850), change_text, fill=change_color, font=font_change)
                else:
                    self._center_text(draw, change_text, 850, font_change, change_color)

            # Timestamp (appears at 8s)
            if t >= 8:
                font_time = self._get_font(36)
                timestamp = datetime.now().strftime("%B %d, %Y • %I:%M %p")
                self._center_text(draw, timestamp, 1750, font_time, secondary)

            frames.append(np.array(canvas))

        # Create video clip from frames
        clips = [ImageClip(frame).with_duration(1/fps).with_start(i/fps) for i, frame in enumerate(frames)]
        video = concatenate_videoclips(clips, method="compose")
        return [video]

    def _create_countdown_video(self, data: Dict[str, Any], config: VideoConfig) -> List:
        """
        Create animated COUNTDOWN video.

        Timeline:
        - 0-2s: "DEADLINE" pulses
        - 2-5s: Days counts down from +5
        - 5-7s: "DAYS REMAINING" fades in
        - 7-10s: Event info appears
        """
        from moviepy import ImageClip, concatenate_videoclips

        frames = []
        duration = config.duration
        fps = config.fps

        days = data.get('days', 0)
        event = data.get('event', 'DEADLINE')
        date = data.get('date', '')

        for frame_num in range(int(duration * fps)):
            t = frame_num / fps
            canvas = self._create_base_canvas()
            draw = ImageDraw.Draw(canvas)

            white = self._hex_to_rgb(self.config.text_color)
            brand = self._hex_to_rgb(self.config.brand_color)
            secondary = self._hex_to_rgb(self.config.secondary_color)

            # "DEADLINE" with pulse effect (0-2s)
            font_label = self._get_font(60, bold=True)
            if t < 2:
                # Pulse effect
                pulse = 0.7 + 0.3 * np.sin(t * np.pi * 3)
                color = tuple(int(c * pulse) for c in brand)
            else:
                color = brand
            self._center_text(draw, "DEADLINE", 300, font_label, color)

            # Days counter (counts down from days+5 to days during 2-5s)
            if t >= 2:
                font_days = self._get_font(350, bold=True)
                if t < 5:
                    progress = (t - 2) / 3
                    display_days = int(days + 5 - (5 * progress))
                else:
                    display_days = days
                self._center_text(draw, str(display_days), 500, font_days, white)

            # "DAYS REMAINING" (fades in 5-7s)
            if t >= 5:
                font_subtitle = self._get_font(60, bold=True)
                if t < 7:
                    alpha = (t - 5) / 2
                    color = tuple(int(c * alpha) for c in secondary)
                else:
                    color = secondary
                self._center_text(draw, "DAYS REMAINING", 900, font_subtitle, color)

            # Event info (appears 7-10s)
            if t >= 7:
                alpha = min(1.0, (t - 7) / 1)
                font_event = self._get_font(48)
                color = tuple(int(c * alpha) for c in white)
                self._center_text(draw, event.upper(), 1050, font_event, color)

                font_date = self._get_font(40)
                color = tuple(int(c * alpha) for c in secondary)
                self._center_text(draw, date, 1150, font_date, color)

            frames.append(np.array(canvas))

        clips = [ImageClip(frame).with_duration(1/fps).with_start(i/fps) for i, frame in enumerate(frames)]
        video = concatenate_videoclips(clips, method="compose")
        return [video]

    def _create_bank_crisis_video(self, data: Dict[str, Any], config: VideoConfig) -> List:
        """
        Create animated BANK_CRISIS video.

        Timeline:
        - 0-1s: Red flash
        - 1-3s: Bank name slams in
        - 3-6s: Price with drop animation
        - 6-9s: "CRISIS" pulses
        - 9-12s: Exposure data appears
        """
        from moviepy import ImageClip, concatenate_videoclips

        frames = []
        duration = config.duration
        fps = config.fps

        bank = data.get('bank', 'BANK')
        price = data.get('price', 0.0)
        change = data.get('change', 0.0)
        exposure = data.get('exposure', '$0')
        loss = data.get('loss', '')

        for frame_num in range(int(duration * fps)):
            t = frame_num / fps
            canvas = self._create_base_canvas()
            draw = ImageDraw.Draw(canvas)

            white = self._hex_to_rgb(self.config.text_color)
            brand = self._hex_to_rgb(self.config.brand_color)
            secondary = self._hex_to_rgb(self.config.secondary_color)

            # Red flash (0-1s)
            if t < 1:
                flash_alpha = 1 - t
                overlay = Image.new('RGB', (self.config.image_width, self.config.image_height), brand)
                canvas = Image.blend(canvas, overlay, flash_alpha * 0.5)
                draw = ImageDraw.Draw(canvas)

            # Red bar and bank name (slams in 1-2s)
            if t >= 1:
                # Draw red bar
                draw.rectangle([(0, 250), (self.config.image_width, 320)], fill=brand)

                font_bank = self._get_font(60, bold=True)
                if t < 2:
                    # Slam effect - scale up
                    scale = 0.5 + 0.5 * (t - 1)
                    size = int(60 * scale)
                    font_bank = self._get_font(size, bold=True)
                self._center_text(draw, bank.upper(), 255, font_bank, white)

            # "CRISIS" label (appears 2s, pulses 6-9s)
            if t >= 2:
                font_crisis = self._get_font(100, bold=True)
                if 6 <= t < 9:
                    pulse = 0.6 + 0.4 * np.sin((t - 6) * np.pi * 2)
                    color = tuple(int(c * pulse) for c in brand)
                else:
                    color = brand
                self._center_text(draw, "CRISIS", 400, font_crisis, color)

            # Price and drop (3-6s)
            if t >= 3:
                font_price = self._get_font(140, bold=True)
                self._center_text(draw, f"${price:.2f}", 550, font_price, white)

                font_change = self._get_font(80, bold=True)
                if t < 6:
                    # Animate the drop percentage
                    progress = (t - 3) / 3
                    display_change = change * progress
                else:
                    display_change = change
                change_text = f"▼ {abs(display_change):.1f}%"
                self._center_text(draw, change_text, 720, font_change, brand)

            # Exposure data (9-12s)
            if t >= 9:
                alpha = min(1.0, (t - 9) / 1)
                font_label = self._get_font(36)
                font_value = self._get_font(60, bold=True)

                color_sec = tuple(int(c * alpha) for c in secondary)
                color_white = tuple(int(c * alpha) for c in white)
                color_brand = tuple(int(c * alpha) for c in brand)

                self._center_text(draw, "SILVER EXPOSURE", 900, font_label, color_sec)
                self._center_text(draw, exposure, 950, font_value, color_white)

                if loss:
                    self._center_text(draw, "POTENTIAL LOSS", 1100, font_label, color_sec)
                    self._center_text(draw, loss, 1150, font_value, color_brand)

            frames.append(np.array(canvas))

        clips = [ImageClip(frame).with_duration(1/fps).with_start(i/fps) for i, frame in enumerate(frames)]
        video = concatenate_videoclips(clips, method="compose")
        return [video]

    def _create_daily_summary_video(self, data: Dict[str, Any], config: VideoConfig) -> List:
        """
        Create animated DAILY_SUMMARY video.

        Timeline:
        - 0-2s: Header appears
        - 2-10s: Each metric appears (2s each)
        - 10-13s: Risk index
        - 13-15s: Hold
        """
        from moviepy import ImageClip, concatenate_videoclips

        frames = []
        duration = config.duration
        fps = config.fps

        silver = data.get('silver', 0.0)
        gold = data.get('gold', 0.0)
        ms = data.get('ms', 0.0)
        vix = data.get('vix', 0.0)
        risk = data.get('risk', 0.0)
        date_str = data.get('date', datetime.now().strftime("%B %d, %Y"))

        metrics = [
            ("SILVER", f"${silver:.2f}"),
            ("GOLD", f"${gold:.2f}"),
            ("MORGAN STANLEY", f"${ms:.2f}"),
            ("VIX", f"{vix:.1f}"),
        ]

        for frame_num in range(int(duration * fps)):
            t = frame_num / fps
            canvas = self._create_base_canvas()
            draw = ImageDraw.Draw(canvas)

            white = self._hex_to_rgb(self.config.text_color)
            brand = self._hex_to_rgb(self.config.brand_color)
            secondary = self._hex_to_rgb(self.config.secondary_color)

            # Header (0-2s fade in)
            font_header = self._get_font(70, bold=True)
            font_date = self._get_font(36)

            if t < 2:
                alpha = t / 2
                color = tuple(int(c * alpha) for c in white)
                color_sec = tuple(int(c * alpha) for c in secondary)
            else:
                color = white
                color_sec = secondary

            self._center_text(draw, "DAILY RECAP", 280, font_header, color)
            self._center_text(draw, date_str, 370, font_date, color_sec)

            # Metrics (2-10s, each metric gets 2s)
            font_label = self._get_font(40)
            font_value = self._get_font(70, bold=True)
            y_start = 500
            y_spacing = 180

            for i, (label, value) in enumerate(metrics):
                metric_start = 2 + (i * 2)
                y = y_start + (i * y_spacing)

                if t >= metric_start:
                    if t < metric_start + 0.5:
                        alpha = (t - metric_start) / 0.5
                    else:
                        alpha = 1.0

                    color_sec = tuple(int(c * alpha) for c in secondary)
                    color_white = tuple(int(c * alpha) for c in white)

                    self._center_text(draw, label, y, font_label, color_sec)
                    self._center_text(draw, value, y + 50, font_value, color_white)

            # Risk index (10-13s)
            if t >= 10:
                risk_y = y_start + (len(metrics) * y_spacing) + 50

                if t < 11:
                    alpha = t - 10
                else:
                    alpha = 1.0

                # Risk color
                if risk < 4:
                    risk_color = (0, 200, 0)
                elif risk < 7:
                    risk_color = (255, 200, 0)
                else:
                    risk_color = brand

                color_sec = tuple(int(c * alpha) for c in secondary)
                color_risk = tuple(int(c * alpha) for c in risk_color)

                self._center_text(draw, "RISK INDEX", risk_y, font_label, color_sec)
                font_risk = self._get_font(100, bold=True)
                self._center_text(draw, f"{risk:.1f}", risk_y + 60, font_risk, color_risk)

            frames.append(np.array(canvas))

        clips = [ImageClip(frame).with_duration(1/fps).with_start(i/fps) for i, frame in enumerate(frames)]
        video = concatenate_videoclips(clips, method="compose")
        return [video]
