import React, { useEffect, useState } from "react";
import Modal from "./Modal";

/**
 * Opens a contact form in a modal. Also opens automatically after 8 s on the help page
 * (product owner request: "proactive support").
 */
export default function ContactDialog({ autoOpen = false }) {
  const [open, setOpen] = useState(false);
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState("");
  const [errors, setErrors] = useState({});

  useEffect(() => {
    if (autoOpen) {
      const t = setTimeout(() => setOpen(true), 8000);
      return () => clearTimeout(t);
    }
  }, [autoOpen]);

  function submit(e) {
    e.preventDefault();
    const errs = {};
    if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) errs.email = true;
    if (!message.trim()) errs.message = true;
    setErrors(errs);
    if (Object.keys(errs).length === 0) {
      fetch("/api/contact", { method: "POST", body: JSON.stringify({ email, message }) });
      setOpen(false);
    }
  }

  return (
    <>
      <button className="btn-primary" onClick={() => setOpen(true)}>
        Contactez-nous
      </button>

      <Modal open={open} onClose={() => setOpen(false)} title="Contactez le support">
        <form onSubmit={submit} noValidate>
          <div className="field">
            <input
              type="text"
              placeholder="Votre adresse e-mail *"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              style={errors.email ? { borderColor: "#d00" } : {}}
            />
          </div>
          <div className="field">
            <textarea
              placeholder="Votre message *"
              rows={5}
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              style={errors.message ? { borderColor: "#d00" } : {}}
            />
          </div>
          {Object.keys(errors).length > 0 && (
            <p className="error">Veuillez corriger les champs en rouge.</p>
          )}
          <button type="submit" className="btn-primary">
            Envoyer
          </button>
        </form>
      </Modal>
    </>
  );
}
