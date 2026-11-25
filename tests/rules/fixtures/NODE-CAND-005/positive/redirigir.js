function ir(app, destino) {
  app.get("/a", (req, res) => res.redirect(destino));
  app.get("/b", (req, res) => res.redirect(req.query.next));
}
