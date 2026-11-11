import { test } from "node:test";
import assert from "node:assert/strict";
import {
  clampPage,
  defaultDoublePage,
  fittedPageWidth,
  visiblePages,
  stepPage,
  thumbnailWindow,
} from "../src/reader/model.ts";
test("cover, spreads and odd/even last pages remain in bounds", () => {
  for (const total of [1, 2, 3, 299, 300]) {
    for (let n = 1; n <= total; n++) {
      for (const double of [false, true]) {
        const pages = visiblePages(n, total, double);
        assert.ok(pages.includes(n));
        assert.ok(
          pages.length <= 2 && pages.every((p) => p >= 1 && p <= total),
        );
        assert.ok(stepPage(n, total, double, 1) <= total);
        assert.ok(stepPage(n, total, double, -1) >= 1);
      }
    }
  }
  assert.deepEqual(visiblePages(1, 300, true), [1]);
  assert.deepEqual(visiblePages(299, 300, true), [298, 299]);
  assert.deepEqual(visiblePages(300, 300, true), [300]);
});
test("input clamps invalid and fractional pages", () => {
  assert.equal(clampPage(NaN, 300), 1);
  assert.equal(clampPage(-1, 300), 1);
  assert.equal(clampPage(900, 300), 300);
  assert.equal(clampPage(2.9, 300), 2);
});
test("reader defaults to two desktop pages and one mobile page", () => {
  assert.equal(defaultDoublePage(false), true);
  assert.equal(defaultDoublePage(true), false);
});
test("page fit fills available height while respecting one- and two-page widths", () => {
  const spreadPage = fittedPageWidth(1000, 900, 2, 0.707);
  assert.ok(spreadPage * 2 + 34 <= 1000);
  assert.ok(spreadPage / 0.707 + 32 <= 900);

  const singlePage = fittedPageWidth(1000, 900, 1, 0.707);
  assert.ok(singlePage + 32 <= 1000);
  assert.ok(singlePage / 0.707 + 32 <= 900);
  assert.ok(singlePage > spreadPage);
});
test("thumbnail virtualization has constant surface count", () => {
  for (let y = 0; y < 16800; y += 100) {
    const pages = thumbnailWindow(y, 300);
    assert.ok(pages.length <= 10 && pages.every((n) => n >= 1 && n <= 300));
  }
});

test("a data editorial usa Brasília mesmo quando o navegador está em UTC", async () => {
  const { publicationToday } = await import("../src/editorial-date.js");
  assert.equal(
    publicationToday(new Date("2026-11-04T01:00:00Z")),
    "2026-11-03",
  );
  assert.equal(
    publicationToday(new Date("2026-11-04T04:00:00Z")),
    "2026-11-04",
  );
});

test("erros de rede do leitor são compreensíveis e não expõem URLs técnicas", async () => {
  const { readerError } = await import("../src/reader/errors.js");
  const message = readerError({
    status: 503,
    message: "Unexpected server response https://private.example/file",
  });
  assert.match(message, /conexão/);
  assert.doesNotMatch(message, /https|Unexpected/);
  assert.match(readerError({ status: 404 }), /não está mais disponível/);
  assert.match(
    readerError({ name: "InvalidPDFException" }),
    /equipe editorial/,
  );
});
