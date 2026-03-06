from dataclasses import dataclass, field


@dataclass
class ItemResult:
    name: str
    kind: str  # "image" or "video"
    original_size: int
    compressed_size: int
    skipped: bool = False

    @property
    def saved(self) -> int:
        return self.original_size - self.compressed_size


@dataclass
class Report:
    input_path: str
    output_path: str
    original_total: int = 0
    compressed_total: int = 0
    items: list[ItemResult] = field(default_factory=list)

    def add(self, item: ItemResult) -> None:
        self.items.append(item)
        self.original_total += item.original_size
        self.compressed_total += item.compressed_size

    @property
    def images(self) -> list[ItemResult]:
        return [i for i in self.items if i.kind == "image" and not i.skipped]

    @property
    def videos(self) -> list[ItemResult]:
        return [i for i in self.items if i.kind == "video" and not i.skipped]

    @property
    def reduction_pct(self) -> float:
        if self.original_total == 0:
            return 0.0
        return (1 - self.compressed_total / self.original_total) * 100


def _fmt(b: int) -> str:
    if b >= 1_000_000:
        return f"{b / 1_000_000:.1f} MB"
    if b >= 1_000:
        return f"{b / 1_000:.1f} KB"
    return f"{b} B"


def print_summary(report: Report, dry_run: bool = False) -> None:
    label = report.input_path
    print(f"Compressing {label}...")

    img_orig = sum(i.original_size for i in report.images)
    img_comp = sum(i.compressed_size for i in report.images)
    if report.images:
        print(f"  Images: {len(report.images)} compressed ({_fmt(img_orig)} → {_fmt(img_comp)})")

    vid_orig = sum(v.original_size for v in report.videos)
    vid_comp = sum(v.compressed_size for v in report.videos)
    if report.videos:
        print(f"  Videos: {len(report.videos)} compressed ({_fmt(vid_orig)} → {_fmt(vid_comp)})")

    if dry_run:
        print(
            f"Dry run: would save {_fmt(report.original_total - report.compressed_total)} "
            f"({report.reduction_pct:.0f}%)"
        )
    else:
        print(
            f"Saved: {report.output_path} "
            f"({_fmt(report.original_total)} → {_fmt(report.compressed_total)}, "
            f"-{report.reduction_pct:.0f}%)"
        )
