const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, PageBreak, HeadingLevel,
  AlignmentType, LevelFormat, Bookmark, InternalHyperlink,
} = require("docx");

const MANUSCRIPT_DIR = path.join(__dirname, "manuscript");
const OUT_PATH = path.join(__dirname, "build", "The-Mothers-Code.docx");

const CHAPTER_FILES = [
  "01-introduction.md",
  "02-chapter1-belief-effect.md",
  "03-chapter2-words-that-build.md",
  "04-chapter3-safety-behind-courage.md",
  "05-chapter4-letting-them-fall.md",
  "06-chapter5-presence-over-perfection.md",
  "07-chapter6-mirror-effect.md",
  "08-chapter7-purpose-before-pressure.md",
  "09-chapter8-the-ripple.md",
  "10-chapter9-repair-reflex.md",
  "11-chapter10-naming-the-storm.md",
  "12-chapter11-comparison-trap.md",
  "13-chapter12-gratitude-habit.md",
  "14-chapter13-small-hands-real-work.md",
  "15-chapter14-screen-in-the-room.md",
  "16-chapter15-waiting-well.md",
  "17-chapter16-question-behind-question.md",
  "18-chapter17-touch-that-tells-truth.md",
  "19-chapter18-rhythm-of-rest.md",
  "20-chapter19-discipline-shift.md",
  "21-chapter20-long-goodbye.md",
  "22-chapter21-village-effect.md",
  "23-quick-reference.md",
  "24-closing-letter.md",
];

function readLines(fname) {
  const raw = fs.readFileSync(path.join(MANUSCRIPT_DIR, fname), "utf-8");
  return raw.split("\n");
}

function parseInline(text) {
  const runs = [];
  const boldParts = text.split(/(\*\*[^*]+?\*\*)/g);
  for (const part of boldParts) {
    if (!part) continue;
    if (/^\*\*[^*]+?\*\*$/.test(part)) {
      runs.push(new TextRun({ text: part.slice(2, -2), bold: true }));
    } else {
      const italicParts = part.split(/(\*[^*]+?\*)/g);
      for (const ip of italicParts) {
        if (!ip) continue;
        if (/^\*[^*]+?\*$/.test(ip)) {
          runs.push(new TextRun({ text: ip.slice(1, -1), italics: true }));
        } else {
          runs.push(new TextRun({ text: ip }));
        }
      }
    }
  }
  return runs.length ? runs : [new TextRun({ text: "" })];
}

function getTitle(fname) {
  for (const raw of readLines(fname)) {
    const s = raw.trim();
    if (s.startsWith("# ")) return s.slice(2);
  }
  return fname;
}

function fileToParagraphs(fname, { firstHeadingBreaksPage = true, bookmarkId = null } = {}) {
  const lines = readLines(fname);
  const paragraphs = [];
  let sawFirstHeading = false;

  for (const raw of lines) {
    const s = raw.trim();
    if (!s || s === "\\newpage" || s === "---") continue;

    if (s.startsWith("# ")) {
      const isFirst = !sawFirstHeading;
      const headingRuns = parseInline(s.slice(2));
      paragraphs.push(new Paragraph({
        heading: HeadingLevel.HEADING_1,
        pageBreakBefore: firstHeadingBreaksPage && isFirst ? true : false,
        children: isFirst && bookmarkId
          ? [new Bookmark({ id: bookmarkId, children: headingRuns })]
          : headingRuns,
      }));
      sawFirstHeading = true;
    } else if (s.startsWith("### ")) {
      paragraphs.push(new Paragraph({
        heading: HeadingLevel.HEADING_2,
        children: parseInline(s.slice(4)),
      }));
    } else if (s.startsWith("## ")) {
      paragraphs.push(new Paragraph({
        heading: HeadingLevel.HEADING_2,
        children: parseInline(s.slice(3)),
      }));
    } else if (s.startsWith("- ")) {
      paragraphs.push(new Paragraph({
        numbering: { reference: "bullets", level: 0 },
        children: parseInline(s.slice(2)),
        spacing: { after: 120 },
      }));
    } else if (/^\d+\.\s+/.test(s)) {
      const stripped = s.replace(/^\d+\.\s+/, "");
      paragraphs.push(new Paragraph({
        numbering: { reference: "numbers", level: 0 },
        children: parseInline(stripped),
        spacing: { after: 120 },
      }));
    } else {
      paragraphs.push(new Paragraph({
        alignment: AlignmentType.JUSTIFIED,
        spacing: { after: 200, line: 276 },
        children: parseInline(s),
      }));
    }
  }
  return paragraphs;
}

function buildTitleAndCopyright() {
  const lines = readLines("00-title-page.md");
  const idx = lines.indexOf("\\newpage");
  const front = lines.slice(0, idx);
  const back = lines.slice(idx + 1);

  let title = "", subtitle = "", tagline = "", byline = "";
  for (const l of front) {
    const s = l.trim();
    if (s.startsWith("# ")) title = s.slice(2);
    else if (s.startsWith("### ")) subtitle = s.slice(4);
    else if (s.startsWith("**") && s.endsWith("**")) byline = s.replace(/\*\*/g, "");
    else if (s.startsWith("*") && s.endsWith("*")) tagline = s.replace(/\*/g, "");
  }

  const titlePageParas = [
    new Paragraph({ spacing: { before: 2000 }, alignment: AlignmentType.CENTER,
      children: [new TextRun({ text: title, bold: true, size: 64 })] }),
    new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 200, after: 400 },
      children: [new TextRun({ text: subtitle, italics: true, size: 32, color: "B0606A" })] }),
    new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 400 },
      children: [new TextRun({ text: tagline, italics: true, size: 22 })] }),
    new Paragraph({ alignment: AlignmentType.CENTER,
      children: [new TextRun({ text: `by ${byline}`, italics: true, size: 24, color: "8C6B34" })] }),
    new Paragraph({ children: [new PageBreak()] }),
  ];

  const copyrightParas = [];
  for (const l of back) {
    const s = l.trim();
    if (!s) continue;
    copyrightParas.push(new Paragraph({
      alignment: AlignmentType.CENTER,
      spacing: { after: 200 },
      children: parseInline(s),
    }));
  }
  copyrightParas.push(new Paragraph({ children: [new PageBreak()] }));

  return [...titlePageParas, ...copyrightParas];
}

function main() {
  const body = [];
  body.push(...buildTitleAndCopyright());

  const entries = CHAPTER_FILES.map((fname, i) => ({
    fname,
    title: getTitle(fname),
    bookmarkId: `sec_${i}`,
  }));

  // Manually built, hyperlinked contents page — a Word *field* TOC only shows
  // content once Word itself computes it, which Kindle's converter never
  // does, so it renders blank in Kindle Previewer. Plain hyperlinks work
  // immediately with no field-computation step required.
  body.push(new Paragraph({
    heading: HeadingLevel.HEADING_1,
    children: [new Bookmark({ id: "toc", children: [new TextRun("Contents")] })],
  }));
  for (const entry of entries) {
    body.push(new Paragraph({
      spacing: { after: 160 },
      children: [new InternalHyperlink({
        anchor: entry.bookmarkId,
        children: [new TextRun({ text: entry.title, style: "Hyperlink" })],
      })],
    }));
  }
  body.push(new Paragraph({ children: [new PageBreak()] }));

  for (const entry of entries) {
    body.push(...fileToParagraphs(entry.fname, { bookmarkId: entry.bookmarkId }));
  }

  const doc = new Document({
    numbering: {
      config: [
        { reference: "bullets", levels: [{ level: 0, format: LevelFormat.BULLET, text: "•",
          alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
        { reference: "numbers", levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.",
          alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
      ],
    },
    styles: {
      default: {
        document: { run: { font: "Georgia", size: 22 } }, // 11pt
      },
      paragraphStyles: [
        { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
          run: { size: 36, bold: true, font: "Georgia", color: "3D2A2B" },
          paragraph: { spacing: { before: 240, after: 240 }, alignment: AlignmentType.CENTER, outlineLevel: 0 } },
        { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
          run: { size: 26, bold: true, font: "Georgia", color: "B0606A" },
          paragraph: { spacing: { before: 260, after: 160 }, outlineLevel: 1 } },
      ],
    },
    sections: [{
      properties: {
        page: {
          size: { width: 12240, height: 15840 },
          margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 },
        },
      },
      children: body,
    }],
  });

  Packer.toBuffer(doc).then((buffer) => {
    fs.mkdirSync(path.dirname(OUT_PATH), { recursive: true });
    fs.writeFileSync(OUT_PATH, buffer);
    console.log("Built:", OUT_PATH);
  });
}

main();
