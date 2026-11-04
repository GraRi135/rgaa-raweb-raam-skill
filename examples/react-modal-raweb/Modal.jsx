import React from "react";
import "./Modal.css";

/**
 * Generic modal used across the portal (cookie notice, session warning, contact form).
 */
export default function Modal({ open, onClose, title, children }) {
  if (!open) return null;

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <span className="modal-title">{title}</span>
          <div className="modal-close" onClick={onClose}>
            <svg width="20" height="20" viewBox="0 0 20 20">
              <path d="M4 4l12 12M16 4L4 16" stroke="currentColor" strokeWidth="2" />
            </svg>
          </div>
        </div>
        <div className="modal-body">{children}</div>
      </div>
    </div>
  );
}
