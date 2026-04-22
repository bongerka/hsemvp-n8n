const text = ($json.text || "").replace(/\r\n/g, "\n").trim();
const chunkSize = 850;
const overlap = 140;

if (!text) {
  return [];
}

const chunks = [];
let cursor = 0;
let chunkIndex = 0;

while (cursor < text.length) {
  const end = Math.min(cursor + chunkSize, text.length);
  const chunkText = text.slice(cursor, end).trim();

  if (chunkText) {
    chunks.push({
      json: {
        chunk_text: chunkText,
        metadata: {
          chunk_index: chunkIndex,
          source_title: $json.title || null,
          category: $json.category || null,
        },
      },
    });
  }

  if (end === text.length) {
    break;
  }

  cursor = Math.max(end - overlap, cursor + 1);
  chunkIndex += 1;
}

return chunks;
