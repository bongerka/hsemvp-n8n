const question = $json.question || $json.text || "";
const matches = Array.isArray($json.matches) ? $json.matches : [];

const context = matches
  .map((match, index) => {
    const title = match.title || "Документ";
    const category = match.category || "general";
    const chunk = match.chunk_text || "";
    return `[${index + 1}] ${title} (${category})\n${chunk}`;
  })
  .join("\n\n");

const systemPrompt = `
Ты AI-помощник администратора клиники.

Разрешено:
- отвечать на административные вопросы
- объяснять цены, режим работы, подготовку к визиту, правила записи
- собирать контакты и пожелания для заявки

Запрещено:
- ставить диагнозы
- давать медицинские рекомендации как врач
- придумывать факты, которых нет в контексте

Если в контексте не хватает данных, честно скажи, что нужно уточнить у администратора клиники.
`.trim();

return [
  {
    json: {
      systemPrompt,
      userPrompt: `Контекст:\n${context}\n\nВопрос пользователя:\n${question}`,
      sources: matches.map((match) => ({
        title: match.title,
        category: match.category,
        similarity: match.similarity,
      })),
    },
  },
];
