import { useRef, useState, type FormEventHandler } from "react";
import toast, { Toaster } from "react-hot-toast";
import { analytics } from "@/utils/analytics";

// Get API URL from environment variable or default
const API_URL = import.meta.env.PUBLIC_API_URL || "http://localhost:8000";

const ContactForm = () => {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const formRef = useRef<HTMLFormElement>(null);

  const handleSubmit: FormEventHandler<HTMLFormElement> = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);

    const formData = new FormData(e.currentTarget);
    const email = formData.get("email") as string;
    const name = formData.get("name") as string;
    const message = formData.get("message") as string;
    const subject = formData.get("subject") as string;

    if (!email) {
      toast.error("Please enter your email");
      setIsSubmitting(false);
      return;
    }

    try {
      // Submit to backend API
      const response = await fetch(`${API_URL}/api/contact/submit`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          name: name || "Anonymous",
          email,
          subject,
          message,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to submit message");
      }

      const result = await response.json();

      // Track successful submission
      analytics.contactFormSubmit(true);

      setIsSubmitting(false);
      toast.success(result.message || "Thanks! I'll be in touch.", {
        duration: 4000,
      });
      formRef.current?.reset();
    } catch (error) {
      console.error("Form submission error:", error);

      // Track failed submission
      analytics.contactFormSubmit(false);

      setIsSubmitting(false);
      toast.error("Failed to send message. Please try again.", {
        duration: 4000,
      });
    }
  };

  return (
    <>
      <form className="contact-form" ref={formRef} onSubmit={handleSubmit}>
        <h2>Let's Connect</h2>
        <p>Reach out below for inquiries, quotes, or collaborations.</p>
        <label>
          Your Name
          <input
            type="text"
            name="name"
            autoComplete="name"
            placeholder="e.g., John Doe"
          />
        </label>
        <label>
          Your Email
          <input
            required
            type="email"
            name="email"
            autoComplete="email"
            placeholder="e.g., katie@email.com"
          />
        </label>
        <label>
          Subject (Optional)
          <input
            type="text"
            name="subject"
            placeholder="e.g., Job Opportunity"
          />
        </label>
        <label>
          Message
          <textarea
            required
            name="message"
            rows={5}
            placeholder="Tell me about your project or inquiry..."
            minLength={10}
          />
        </label>
        <button className="link" type="submit" disabled={isSubmitting}>
          {isSubmitting ? "Submitting…" : "Send Message"}
        </button>
      </form>
      <Toaster />
    </>
  );
};

export default ContactForm;
