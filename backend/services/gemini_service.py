import os
import json
import logging
import re
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Configure Gemini API
API_KEY = os.environ.get("GEMINI_" + "API_KEY")
if API_KEY and API_KEY != "YOUR_GEMINI_API_KEY_HERE":
    genai.configure(api_key=API_KEY)
else:
    logger.warning("GEMINI_API_KEY environment variable is not set. Using local mock generator fallback.")

def generate_portfolio(resume_text, theme):
    """
    Sends the resume text to Google Gemini and returns a dict with 'html' and 'css'.
    Falls back to a premium local mock portfolio generator if API key is not set.
    """
    # Check if API_KEY is set and is valid
    is_mock = False
    if not API_KEY or API_KEY == "YOUR_GEMINI_API_KEY_HERE":
        logger.warning("No valid Gemini API key found. Falling back to high-quality mock portfolio generation.")
        is_mock = True

    if is_mock:
        return _get_mock_portfolio(resume_text, theme)

    # Select the model. Using gemini-1.5-flash for code generation and speed.
    model_name = "gemini-1.5-flash"
    
    # Theme descriptions to steer Gemini's CSS generation
    theme_guidelines = {
        "Modern Developer": (
            "A dark mode theme with neon accents (e.g. glowing cyan, electric purple, or lime green). "
            "Use modern layout elements, developer-friendly monospace fonts for headers/code blocks, "
            "smooth scaling on hover, rounded border-radius for badges and cards, and glowing box-shadows."
        ),
        "Glassmorphism": (
            "A modern futuristic design using frosted glass panels. "
            "Use a soft gradient background (e.g., violet-to-blue or dark indigo) with large blur shapes. "
            "Give sections and cards a background like `rgba(255, 255, 255, 0.05)`, border `1px solid rgba(255, 255, 255, 0.1)`, "
            "and `backdrop-filter: blur(12px)`. Typography should be elegant and readable."
        ),
        "Professional Corporate": (
            "A sleek, polished corporate design using professional blue, slate gray, and crisp white/dark-blue backgrounds. "
            "Use standard geometric grid systems, structured timeline indicators for education and experience, "
            "clean sans-serif typography (e.g., Inter, Helvetica), and thin dividers. The look should feel highly trustworthy and corporate."
        ),
        "Minimal Clean": (
            "A minimalist monochromatic theme prioritizing whitespace, typography, and contrast. "
            "Use black, white, and varying shades of gray. Avoid colorful backgrounds or gradients. "
            "Emphasize strong, bold text headers and elegant layout proportions. Borders should be extremely thin or non-existent."
        )
    }

    selected_theme_guide = theme_guidelines.get(theme, theme_guidelines["Modern Developer"])

    # Base prompt system instruction
    prompt = f"""You are an expert portfolio website generator.
Analyze the resume text provided below and create a stunning, professional, and fully responsive single-page portfolio website.

Requirements for the generated code:
1. The website must include the following sections:
   - Hero Section (with name, title/headline, and a high-impact intro)
   - About Section (professional summary of their background)
   - Skills Section (categorized skill tags/badges)
   - Projects Section (cards representing their key projects or experiences)
   - Experience Section (work history timeline)
   - Education Section (academic qualifications)
   - Achievements Section (honors, certificates, or accomplishments)
   - Contact Section (with social links, professional email, and a styled mockup contact form)
2. Use modern HTML5 semantic elements (e.g., <header>, <nav>, <main>, <section>, <footer>, <article>).
3. The HTML should NOT contain any inline style attributes or `<style>` blocks. It must link to the external CSS using exactly: `<link rel="stylesheet" href="style.css">`.
4. Include icons where appropriate (you can use standard Unicode emojis or embed a FontAwesome link in the HTML header, e.g. `<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">`).
5. Design theme: {theme}.
   Specific theme styling instructions: {selected_theme_guide}
6. Ensure that all generated content is extracted and polished from the candidate's resume. Do not use generic placeholder names like [Your Name]; fill in actual resume details. If information for a section is missing from the resume, write high-quality professional default copy based on the candidate's profile, or create elegant layout blocks that represent their background.
7. Return a valid JSON response containing exactly two fields: "html" and "css". Do not return any other text, markdown blocks, or surrounding wrappers outside of the JSON object.

Format the output strictly as a JSON object:
{{
  "html": "The full HTML code starting with <!DOCTYPE html> and ending with </html>",
  "css": "The full CSS code"
}}

Resume Text:
{resume_text}
"""

    try:
        model = genai.GenerativeModel(model_name)
        
        # Call the API with JSON response mime type configuration
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        
        response_text = response.text.strip()
        data = json.loads(response_text)
        
        if "html" not in data or "css" not in data:
            raise KeyError("JSON response must contain 'html' and 'css' keys")
            
        return data
        
    except json.JSONDecodeError as je:
        logger.error(f"Failed to parse JSON response from Gemini: {response_text}")
        raise ValueError("AI generated output was not in the expected JSON format. Please try again.") from je
    except Exception as e:
        logger.error(f"Error generating portfolio: {str(e)}")
        raise e


def _extract_name_and_role(text):
    """
    Extracts name and a likely role from resume text.
    """
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    name = "Alex Morgan"
    role = "Full-Stack Software Engineer"
    
    # Try to grab first line as name
    if lines:
        for line in lines[:3]:
            # Clean name from email/phone line
            if "@" not in line and "+" not in line and len(line) < 40 and not line.lower().startswith("resume"):
                name = line
                break
                
    # Search for common developer words for role
    text_lower = text.lower()
    if "data scientist" in text_lower or "machine learning" in text_lower:
        role = "Machine Learning Engineer"
    elif "frontend" in text_lower or "front-end" in text_lower:
        role = "Frontend Web Developer"
    elif "backend" in text_lower or "back-end" in text_lower:
        role = "Backend Systems Engineer"
    elif "product manager" in text_lower:
        role = "Technical Product Manager"
    elif "designer" in text_lower or "ux" in text_lower:
        role = "UX/UI Designer"
        
    return name, role


def _get_mock_portfolio(resume_text, theme):
    """
    Returns a highly polished, theme-specific, static mock portfolio based on resume text.
    """
    name, role = _extract_name_and_role(resume_text)
    
    # Construct fallback HTML structure
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{name} - Portfolio</title>
    <link rel="stylesheet" href="style.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
</head>
<body>
    <header>
        <div class="logo">{name[0]}<span>.</span></div>
        <nav>
            <a href="#hero">Home</a>
            <a href="#about">About</a>
            <a href="#skills">Skills</a>
            <a href="#projects">Projects</a>
            <a href="#experience">Experience</a>
            <a href="#contact">Contact</a>
        </nav>
    </header>

    <main>
        <section id="hero" class="hero-section">
            <div class="hero-content">
                <p class="hero-intro">Hello, I'm</p>
                <h1>{name}</h1>
                <h2>{role}</h2>
                <p class="hero-tagline">Building modern, scalable, and highly interactive digital experiences.</p>
                <div class="hero-actions">
                    <a href="#contact" class="btn btn-primary">Get In Touch</a>
                    <a href="#projects" class="btn btn-secondary">View Work</a>
                </div>
            </div>
        </section>

        <section id="about" class="about-section">
            <h2 class="section-title">About Me</h2>
            <div class="about-content">
                <div class="about-text">
                    <p>I am a passionate and dedicated professional specializing in designing and developing high-quality web applications. With years of experience solving complex problems, I love translating user needs into clean, robust, and beautiful code interfaces.</p>
                    <p>My approach is focused on user experience, performant codebases, and maintainable project structures. I stay up-to-date with emerging tools and technologies to always deliver top-tier solutions.</p>
                </div>
            </div>
        </section>

        <section id="skills" class="skills-section">
            <h2 class="section-title">My Expertise</h2>
            <div class="skills-grid">
                <div class="skill-category">
                    <h3>Frontend Development</h3>
                    <div class="skill-tags">
                        <span class="skill-tag">HTML5 / CSS3</span>
                        <span class="skill-tag">JavaScript (ES6+)</span>
                        <span class="skill-tag">React / Next.js</span>
                        <span class="skill-tag">Tailwind CSS</span>
                    </div>
                </div>
                <div class="skill-category">
                    <h3>Backend & Devops</h3>
                    <div class="skill-tags">
                        <span class="skill-tag">Node.js / Express</span>
                        <span class="skill-tag">Python / Flask</span>
                        <span class="skill-tag">PostgreSQL / MongoDB</span>
                        <span class="skill-tag">Docker & AWS</span>
                    </div>
                </div>
            </div>
        </section>

        <section id="projects" class="projects-section">
            <h2 class="section-title">Featured Projects</h2>
            <div class="projects-grid">
                <article class="project-card">
                    <div class="project-icon"><i class="fa-solid fa-code"></i></div>
                    <h3>Intelligent System Dashboard</h3>
                    <p>Designed a responsive analytical admin dashboard parsing complex metrics and rendering SVG interactive charts in real time.</p>
                    <div class="project-tags">
                        <span class="p-tag">React</span>
                        <span class="p-tag">D3.js</span>
                        <span class="p-tag">Tailwind</span>
                    </div>
                </article>
                <article class="project-card">
                    <div class="project-icon"><i class="fa-solid fa-database"></i></div>
                    <h3>E-Commerce Microservices API</h3>
                    <p>Built a secure, containerized microservices database API supporting lightning-fast queries, Redis caching, and stripe payments integrations.</p>
                    <div class="project-tags">
                        <span class="p-tag">Flask</span>
                        <span class="p-tag">Redis</span>
                        <span class="p-tag">Postgres</span>
                    </div>
                </article>
            </div>
        </section>

        <section id="experience" class="experience-section">
            <h2 class="section-title">Work History</h2>
            <div class="timeline">
                <div class="timeline-item">
                    <div class="timeline-dot"></div>
                    <div class="timeline-date">2023 - Present</div>
                    <h3 class="timeline-role">Lead Full-Stack Developer</h3>
                    <h4 class="timeline-company">Global Tech Solutions</h4>
                    <p>Pioneered frontend architectures, decreasing load times by 30%. Mentored junior engineers and designed internal component libraries.</p>
                </div>
                <div class="timeline-item">
                    <div class="timeline-dot"></div>
                    <div class="timeline-date">2021 - 2023</div>
                    <h3 class="timeline-role">Software Engineer</h3>
                    <h4 class="timeline-company">Innovate Web Labs</h4>
                    <p>Built scalable APIs and databases using Python and Node.js. Maintained 99.9% app uptime by integrating robust automated testing pipelines.</p>
                </div>
            </div>
        </section>

        <section id="contact" class="contact-section">
            <h2 class="section-title">Let's Connect</h2>
            <div class="contact-container">
                <div class="contact-info">
                    <p>Interested in working together? Drop me a message and let's construct something awesome.</p>
                    <div class="contact-links">
                        <a href="mailto:hello@example.com"><i class="fa-regular fa-envelope"></i> hello@example.com</a>
                        <a href="https://github.com"><i class="fa-brands fa-github"></i> GitHub Profile</a>
                        <a href="https://linkedin.com"><i class="fa-brands fa-linkedin"></i> LinkedIn Profile</a>
                    </div>
                </div>
                <form class="contact-form" onsubmit="event.preventDefault(); alert('Message sent successfully! (Mock submission)');">
                    <input type="text" placeholder="Your Name" required>
                    <input type="email" placeholder="Your Email" required>
                    <textarea placeholder="Your Message" rows="4" required></textarea>
                    <button type="submit" class="btn btn-primary">Send Message</button>
                </form>
            </div>
        </section>
    </main>

    <footer>
        <p>&copy; 2026 {name}. All rights reserved.</p>
    </footer>
</body>
</html>
"""

    # Theme CSS selectors
    if theme == "Glassmorphism":
        css = """@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');

* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
    scroll-behavior: smooth;
}

body {
    background: linear-gradient(135deg, #1e1b4b 0%, #311042 50%, #0c0a24 100%);
    color: #f8fafc;
    font-family: 'Outfit', sans-serif;
    min-height: 100vh;
    background-attachment: fixed;
    line-height: 1.6;
}

header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1.5rem 10%;
    background: rgba(255, 255, 255, 0.03);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    position: fixed;
    width: 100%;
    top: 0;
    z-index: 100;
}

.logo {
    font-size: 1.5rem;
    font-weight: 700;
    letter-spacing: -1px;
}

.logo span {
    color: #ec4899;
}

nav a {
    color: #cbd5e1;
    text-decoration: none;
    margin-left: 2rem;
    font-weight: 500;
    font-size: 0.95rem;
    transition: color 0.3s;
}

nav a:hover {
    color: #ec4899;
}

main {
    padding-top: 80px;
    max-width: 1100px;
    margin: 0 auto;
    padding-left: 2rem;
    padding-right: 2rem;
}

section {
    padding: 6rem 0;
}

.section-title {
    font-size: 2.25rem;
    font-weight: 700;
    margin-bottom: 3rem;
    text-align: center;
    position: relative;
}

.section-title::after {
    content: '';
    position: absolute;
    bottom: -12px;
    left: 50%;
    transform: translateX(-50%);
    width: 60px;
    height: 4px;
    background: linear-gradient(90deg, #ec4899, #3b82f6);
    border-radius: 2px;
}

/* Glass panel base */
.about-content, .skill-category, .project-card, .timeline-item, .contact-container, .contact-form input, .contact-form textarea {
    background: rgba(255, 255, 255, 0.04);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 16px;
    padding: 2rem;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.2);
}

/* Hero */
.hero-section {
    min-height: 80vh;
    display: flex;
    align-items: center;
    justify-content: center;
    text-align: center;
}

.hero-intro {
    color: #ec4899;
    font-size: 1.1rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 2px;
    margin-bottom: 1rem;
}

.hero-section h1 {
    font-size: 4rem;
    font-weight: 800;
    margin-bottom: 1rem;
    background: linear-gradient(135deg, #fff 30%, #a5b4fc 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.hero-section h2 {
    font-size: 2rem;
    color: #cbd5e1;
    font-weight: 500;
    margin-bottom: 1.5rem;
}

.hero-tagline {
    font-size: 1.15rem;
    color: #94a3b8;
    max-width: 600px;
    margin: 0 auto 2.5rem;
}

.hero-actions {
    display: flex;
    justify-content: center;
    gap: 1.5rem;
}

.btn {
    padding: 0.75rem 2rem;
    font-size: 0.95rem;
    font-weight: 600;
    border-radius: 30px;
    text-decoration: none;
    transition: all 0.3s;
}

.btn-primary {
    background: linear-gradient(135deg, #ec4899 0%, #3b82f6 100%);
    color: white;
    border: none;
    box-shadow: 0 4px 20px rgba(236, 72, 153, 0.3);
}

.btn-primary:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 25px rgba(236, 72, 153, 0.5);
}

.btn-secondary {
    background: rgba(255, 255, 255, 0.05);
    color: #f8fafc;
    border: 1px solid rgba(255, 255, 255, 0.1);
}

.btn-secondary:hover {
    background: rgba(255, 255, 255, 0.1);
    transform: translateY(-2px);
}

/* Skills */
.skills-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 2rem;
}

.skill-category h3 {
    font-size: 1.25rem;
    margin-bottom: 1.5rem;
    color: #ec4899;
}

.skill-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 0.75rem;
}

.skill-tag {
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.05);
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 0.85rem;
}

/* Projects */
.projects-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
    gap: 2rem;
}

.project-card {
    transition: transform 0.3s, border-color 0.3s;
}

.project-card:hover {
    transform: translateY(-5px);
    border-color: rgba(236, 72, 153, 0.3);
}

.project-icon {
    font-size: 2rem;
    color: #3b82f6;
    margin-bottom: 1.25rem;
}

.project-card h3 {
    font-size: 1.35rem;
    margin-bottom: 0.75rem;
}

.project-card p {
    color: #94a3b8;
    font-size: 0.95rem;
    margin-bottom: 1.5rem;
}

.project-tags {
    display: flex;
    gap: 0.5rem;
}

.p-tag {
    font-size: 0.75rem;
    color: #ec4899;
    background: rgba(236, 72, 153, 0.1);
    padding: 2px 8px;
    border-radius: 4px;
    font-weight: 500;
}

/* Experience */
.timeline {
    display: flex;
    flex-direction: column;
    gap: 2rem;
    max-width: 700px;
    margin: 0 auto;
}

.timeline-item {
    position: relative;
    padding-left: 2.5rem;
}

.timeline-dot {
    position: absolute;
    left: 1.25rem;
    top: 2.3rem;
    width: 12px;
    height: 12px;
    background: #ec4899;
    border-radius: 50%;
    box-shadow: 0 0 10px #ec4899;
}

.timeline-date {
    font-size: 0.85rem;
    color: #3b82f6;
    font-weight: 600;
    margin-bottom: 0.5rem;
}

.timeline-role {
    font-size: 1.2rem;
    margin-bottom: 0.25rem;
}

.timeline-company {
    font-size: 0.95rem;
    color: #cbd5e1;
    margin-bottom: 0.75rem;
}

.timeline-item p {
    font-size: 0.9rem;
    color: #94a3b8;
}

/* Contact */
.contact-container {
    display: grid;
    grid-template-columns: 1fr 1.2fr;
    gap: 3rem;
}

@media (max-width: 768px) {
    .contact-container {
        grid-template-columns: 1fr;
    }
}

.contact-info {
    display: flex;
    flex-direction: column;
    justify-content: center;
}

.contact-info p {
    font-size: 1.1rem;
    color: #cbd5e1;
    margin-bottom: 2rem;
}

.contact-links {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.contact-links a {
    color: #f8fafc;
    text-decoration: none;
    font-size: 1rem;
    display: flex;
    align-items: center;
    gap: 10px;
}

.contact-links a:hover {
    color: #ec4899;
}

.contact-form {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    padding: 2rem;
}

.contact-form input, .contact-form textarea {
    width: 100%;
    padding: 10px 16px;
    color: white;
    outline: none;
    border-radius: 8px;
    font-family: inherit;
}

.contact-form input:focus, .contact-form textarea:focus {
    border-color: #ec4899;
}

.contact-form button {
    cursor: pointer;
    align-self: flex-start;
}

footer {
    text-align: center;
    padding: 3rem 0;
    border-top: 1px solid rgba(255, 255, 255, 0.05);
    color: #64748b;
    font-size: 0.9rem;
}
"""
    elif theme == "Professional Corporate":
        css = """@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
    scroll-behavior: smooth;
}

body {
    background-color: #f8fafc;
    color: #1e293b;
    font-family: 'Inter', sans-serif;
    line-height: 1.6;
}

header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1.25rem 8%;
    background-color: #ffffff;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
    position: fixed;
    width: 100%;
    top: 0;
    z-index: 100;
}

.logo {
    font-size: 1.35rem;
    font-weight: 700;
    color: #1e3a8a;
}

.logo span {
    color: #3b82f6;
}

nav a {
    color: #475569;
    text-decoration: none;
    margin-left: 2rem;
    font-weight: 500;
    font-size: 0.95rem;
    transition: color 0.2s;
}

nav a:hover {
    color: #1e3a8a;
}

main {
    padding-top: 75px;
}

section {
    padding: 5rem 8%;
    border-bottom: 1px solid #e2e8f0;
}

section:nth-of-type(even) {
    background-color: #f1f5f9;
}

.section-title {
    font-size: 1.85rem;
    font-weight: 700;
    color: #0f172a;
    margin-bottom: 2.5rem;
    position: relative;
}

.section-title::after {
    content: '';
    position: absolute;
    bottom: -8px;
    left: 0;
    width: 40px;
    height: 3px;
    background-color: #1e3a8a;
}

/* Hero */
.hero-section {
    padding-top: 8rem;
    padding-bottom: 8rem;
    background: linear-gradient(135deg, #1e3a8a 0%, #0f172a 100%);
    color: #ffffff;
    border: none;
    text-align: left;
}

.hero-intro {
    color: #93c5fd;
    font-size: 0.95rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin-bottom: 1rem;
}

.hero-section h1 {
    font-size: 3.5rem;
    font-weight: 800;
    line-height: 1.15;
    margin-bottom: 1rem;
}

.hero-section h2 {
    font-size: 1.75rem;
    color: #cbd5e1;
    font-weight: 400;
    margin-bottom: 1.5rem;
}

.hero-tagline {
    font-size: 1.1rem;
    color: #94a3b8;
    max-width: 650px;
    margin-bottom: 2.5rem;
}

.hero-actions {
    display: flex;
    gap: 1rem;
}

.btn {
    padding: 0.75rem 1.75rem;
    font-size: 0.95rem;
    font-weight: 600;
    border-radius: 4px;
    text-decoration: none;
    transition: all 0.2s;
}

.btn-primary {
    background-color: #3b82f6;
    color: white;
    border: 1px solid #3b82f6;
}

.btn-primary:hover {
    background-color: #2563eb;
    border-color: #2563eb;
}

.btn-secondary {
    background-color: transparent;
    color: #ffffff;
    border: 1px solid rgba(255, 255, 255, 0.4);
}

.btn-secondary:hover {
    border-color: #ffffff;
    background-color: rgba(255, 255, 255, 0.05);
}

/* About */
.about-content {
    max-width: 800px;
}

.about-text p {
    font-size: 1.05rem;
    color: #334155;
    margin-bottom: 1rem;
}

/* Skills */
.skills-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 2rem;
}

.skill-category {
    background: #ffffff;
    padding: 1.75rem;
    border-radius: 4px;
    border: 1px solid #e2e8f0;
}

.skill-category h3 {
    font-size: 1.1rem;
    color: #1e3a8a;
    margin-bottom: 1.25rem;
    border-bottom: 2px solid #f1f5f9;
    padding-bottom: 0.5rem;
}

.skill-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
}

.skill-tag {
    background: #f1f5f9;
    color: #334155;
    padding: 4px 10px;
    border-radius: 4px;
    font-size: 0.85rem;
    font-weight: 500;
}

/* Projects */
.projects-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 2rem;
}

.project-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 4px;
    padding: 2rem;
    transition: transform 0.2s, box-shadow 0.2s;
}

.project-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.project-icon {
    font-size: 1.75rem;
    color: #1e3a8a;
    margin-bottom: 1rem;
}

.project-card h3 {
    font-size: 1.25rem;
    margin-bottom: 0.5rem;
}

.project-card p {
    color: #475569;
    font-size: 0.9rem;
    margin-bottom: 1.25rem;
}

.project-tags {
    display: flex;
    gap: 0.5rem;
}

.p-tag {
    font-size: 0.75rem;
    color: #1e3a8a;
    background: #eff6ff;
    padding: 2px 6px;
    border-radius: 2px;
    font-weight: 600;
}

/* Experience */
.timeline {
    border-left: 2px solid #e2e8f0;
    padding-left: 1.5rem;
    margin-left: 1rem;
    max-width: 800px;
}

.timeline-item {
    position: relative;
    margin-bottom: 2rem;
}

.timeline-item:last-child {
    margin-bottom: 0;
}

.timeline-dot {
    position: absolute;
    left: -24px;
    top: 6px;
    width: 14px;
    height: 14px;
    background-color: #1e3a8a;
    border: 3px solid #ffffff;
    border-radius: 50%;
}

.timeline-date {
    font-size: 0.85rem;
    color: #3b82f6;
    font-weight: 700;
    margin-bottom: 0.25rem;
}

.timeline-role {
    font-size: 1.15rem;
    color: #0f172a;
}

.timeline-company {
    font-size: 0.9rem;
    color: #475569;
    font-weight: 600;
    margin-bottom: 0.5rem;
}

.timeline-item p {
    font-size: 0.9rem;
    color: #475569;
}

/* Contact */
.contact-container {
    display: grid;
    grid-template-columns: 1fr 1.2fr;
    gap: 4rem;
}

@media (max-width: 768px) {
    .contact-container {
        grid-template-columns: 1fr;
        gap: 2rem;
    }
}

.contact-info p {
    font-size: 1rem;
    color: #334155;
    margin-bottom: 1.5rem;
}

.contact-links {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
}

.contact-links a {
    color: #1e3a8a;
    text-decoration: none;
    font-weight: 500;
    display: flex;
    align-items: center;
    gap: 8px;
}

.contact-links a:hover {
    text-decoration: underline;
}

.contact-form {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.contact-form input, .contact-form textarea {
    width: 100%;
    padding: 10px 14px;
    border: 1px solid #cbd5e1;
    border-radius: 4px;
    font-family: inherit;
    font-size: 0.9rem;
    outline: none;
}

.contact-form input:focus, .contact-form textarea:focus {
    border-color: #1e3a8a;
    box-shadow: 0 0 0 2px rgba(30, 58, 138, 0.1);
}

.contact-form button {
    cursor: pointer;
    align-self: flex-start;
}

footer {
    text-align: center;
    padding: 2.5rem 0;
    color: #64748b;
    background-color: #0f172a;
    color: #94a3b8;
    font-size: 0.85rem;
}
"""
    elif theme == "Minimal Clean":
        css = """@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;700&display=swap');

* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
    scroll-behavior: smooth;
}

body {
    background-color: #ffffff;
    color: #111111;
    font-family: 'Space Grotesk', sans-serif;
    line-height: 1.6;
}

header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 2rem 5%;
    position: absolute;
    width: 100%;
    top: 0;
    left: 0;
}

.logo {
    font-size: 1.5rem;
    font-weight: 700;
    letter-spacing: -0.5px;
}

nav a {
    color: #555555;
    text-decoration: none;
    margin-left: 2rem;
    font-size: 0.9rem;
    font-weight: 500;
    transition: color 0.2s;
}

nav a:hover {
    color: #111111;
}

main {
    max-width: 800px;
    margin: 0 auto;
    padding: 0 2rem;
}

section {
    padding: 6rem 0;
    border-bottom: 1px solid #eaeaea;
}

section:last-of-type {
    border-bottom: none;
}

.section-title {
    font-size: 1.75rem;
    font-weight: 700;
    margin-bottom: 2.5rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* Hero */
.hero-section {
    min-height: 90vh;
    display: flex;
    align-items: center;
    border-bottom: 1px solid #eaeaea;
    padding-top: 120px;
}

.hero-intro {
    font-size: 0.95rem;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: #777777;
    margin-bottom: 1rem;
}

.hero-section h1 {
    font-size: 3.5rem;
    font-weight: 700;
    letter-spacing: -1.5px;
    line-height: 1.1;
    margin-bottom: 1rem;
}

.hero-section h2 {
    font-size: 1.75rem;
    color: #555555;
    font-weight: 400;
    margin-bottom: 1.5rem;
}

.hero-tagline {
    font-size: 1.1rem;
    color: #666666;
    margin-bottom: 2.5rem;
}

.hero-actions {
    display: flex;
    gap: 1rem;
}

.btn {
    padding: 0.75rem 1.5rem;
    font-size: 0.9rem;
    font-weight: 500;
    text-decoration: none;
    transition: all 0.2s;
}

.btn-primary {
    background-color: #111111;
    color: #ffffff;
}

.btn-primary:hover {
    background-color: #333333;
}

.btn-secondary {
    background-color: transparent;
    color: #111111;
    border: 1px solid #111111;
}

.btn-secondary:hover {
    background-color: #f5f5f5;
}

/* About */
.about-text p {
    font-size: 1.05rem;
    color: #444444;
    margin-bottom: 1.25rem;
}

/* Skills */
.skills-grid {
    display: flex;
    flex-direction: column;
    gap: 2rem;
}

.skill-category h3 {
    font-size: 1.05rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 1rem;
    color: #666666;
}

.skill-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 0.75rem;
}

.skill-tag {
    border: 1px solid #e1e1e1;
    padding: 6px 14px;
    font-size: 0.85rem;
}

/* Projects */
.projects-grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: 3rem;
}

.project-card {
    border-bottom: 1px solid #eaeaea;
    padding-bottom: 2rem;
}

.project-card:last-child {
    border-bottom: none;
    padding-bottom: 0;
}

.project-icon {
    display: none; /* Hide icons in minimal theme */
}

.project-card h3 {
    font-size: 1.4rem;
    margin-bottom: 0.5rem;
    font-weight: 500;
}

.project-card p {
    color: #555555;
    font-size: 0.95rem;
    margin-bottom: 1.25rem;
}

.project-tags {
    display: flex;
    gap: 0.75rem;
}

.p-tag {
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: #777777;
}

/* Experience */
.timeline {
    display: flex;
    flex-direction: column;
    gap: 2.5rem;
}

.timeline-item {
    display: grid;
    grid-template-columns: 120px 1fr;
    gap: 1.5rem;
}

@media (max-width: 600px) {
    .timeline-item {
        grid-template-columns: 1fr;
        gap: 0.5rem;
    }
}

.timeline-dot {
    display: none;
}

.timeline-date {
    font-size: 0.9rem;
    color: #666666;
    font-weight: 500;
}

.timeline-role {
    font-size: 1.2rem;
    font-weight: 500;
    margin-bottom: 0.25rem;
}

.timeline-company {
    font-size: 0.95rem;
    color: #555555;
    margin-bottom: 0.75rem;
}

.timeline-item p {
    font-size: 0.95rem;
    color: #555555;
}

/* Contact */
.contact-container {
    display: grid;
    grid-template-columns: 1fr;
    gap: 2.5rem;
}

.contact-info p {
    font-size: 1.05rem;
    color: #444444;
    margin-bottom: 1.5rem;
}

.contact-links {
    display: flex;
    gap: 1.5rem;
    flex-wrap: wrap;
}

.contact-links a {
    color: #111111;
    text-decoration: underline;
    font-size: 0.95rem;
}

.contact-links a:hover {
    color: #555555;
}

.contact-form {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    max-width: 500px;
    margin-top: 1rem;
}

.contact-form input, .contact-form textarea {
    width: 100%;
    padding: 12px 0;
    border: none;
    border-bottom: 1px solid #111111;
    font-family: inherit;
    font-size: 0.95rem;
    outline: none;
}

.contact-form button {
    cursor: pointer;
    align-self: flex-start;
    margin-top: 1rem;
}

footer {
    text-align: center;
    padding: 4rem 0;
    color: #888888;
    font-size: 0.8rem;
    border-top: 1px solid #eaeaea;
}
"""
    else: # Modern Developer (default)
        css = """@import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500;600&family=Outfit:wght@400;600;800&display=swap');

* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
    scroll-behavior: smooth;
}

body {
    background-color: #0b0f19;
    color: #f8fafc;
    font-family: 'Outfit', sans-serif;
    line-height: 1.6;
}

header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1.5rem 8%;
    background-color: rgba(11, 15, 25, 0.8);
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
    position: fixed;
    width: 100%;
    top: 0;
    z-index: 100;
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.logo {
    font-size: 1.5rem;
    font-weight: 800;
    font-family: 'Fira Code', monospace;
    color: #06b6d4;
}

.logo span {
    color: #8b5cf6;
}

nav a {
    color: #94a3b8;
    text-decoration: none;
    margin-left: 2rem;
    font-weight: 500;
    font-size: 0.95rem;
    transition: color 0.3s;
}

nav a:hover {
    color: #06b6d4;
}

main {
    padding-top: 80px;
    max-width: 1200px;
    margin: 0 auto;
    padding-left: 1.5rem;
    padding-right: 1.5rem;
}

section {
    padding: 6rem 0;
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.section-title {
    font-size: 2.25rem;
    font-family: 'Fira Code', monospace;
    font-weight: 700;
    margin-bottom: 3.25rem;
    color: #ffffff;
    display: flex;
    align-items: center;
    gap: 10px;
}

.section-title::before {
    content: 'const ';
    color: #8b5cf6;
    font-size: 1.2rem;
}

.section-title::after {
    content: ' = () => {';
    color: #94a3b8;
    font-size: 1.2rem;
}

/* Hero */
.hero-section {
    min-height: 85vh;
    display: flex;
    align-items: center;
    position: relative;
}

.hero-intro {
    font-family: 'Fira Code', monospace;
    color: #06b6d4;
    font-size: 1rem;
    margin-bottom: 1rem;
}

.hero-section h1 {
    font-size: 4.5rem;
    font-weight: 800;
    line-height: 1.1;
    margin-bottom: 1rem;
    letter-spacing: -1.5px;
}

.hero-section h2 {
    font-size: 2.25rem;
    color: #94a3b8;
    font-weight: 600;
    margin-bottom: 2rem;
}

.hero-tagline {
    font-size: 1.15rem;
    color: #64748b;
    max-width: 650px;
    margin-bottom: 2.5rem;
}

.hero-actions {
    display: flex;
    gap: 1.5rem;
}

.btn {
    padding: 0.75rem 2rem;
    font-size: 0.95rem;
    font-weight: 600;
    border-radius: 8px;
    text-decoration: none;
    transition: all 0.3s;
    display: inline-flex;
    align-items: center;
    gap: 8px;
}

.btn-primary {
    background-color: #06b6d4;
    color: #0b0f19;
    box-shadow: 0 4px 14px rgba(6, 182, 212, 0.4);
}

.btn-primary:hover {
    background-color: #22d3ee;
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(6, 182, 212, 0.6);
}

.btn-secondary {
    background-color: transparent;
    color: #ffffff;
    border: 1px solid rgba(255, 255, 255, 0.2);
}

.btn-secondary:hover {
    border-color: #06b6d4;
    background-color: rgba(6, 182, 212, 0.05);
    transform: translateY(-2px);
}

/* About */
.about-content {
    max-width: 850px;
}

.about-text p {
    font-size: 1.1rem;
    color: #94a3b8;
    margin-bottom: 1.5rem;
}

/* Skills */
.skills-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
    gap: 2.5rem;
}

.skill-category {
    background-color: #121824;
    border: 1px solid rgba(255, 255, 255, 0.05);
    padding: 2rem;
    border-radius: 12px;
}

.skill-category h3 {
    font-family: 'Fira Code', monospace;
    font-size: 1.25rem;
    margin-bottom: 1.5rem;
    color: #8b5cf6;
}

.skill-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 0.75rem;
}

.skill-tag {
    background-color: #1a2234;
    color: #06b6d4;
    border: 1px solid rgba(6, 182, 212, 0.15);
    padding: 6px 14px;
    border-radius: 6px;
    font-size: 0.85rem;
    font-family: 'Fira Code', monospace;
}

/* Projects */
.projects-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(340px, 1fr));
    gap: 2rem;
}

.project-card {
    background-color: #121824;
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 12px;
    padding: 2.25rem;
    transition: all 0.3s;
    position: relative;
    overflow: hidden;
}

.project-card:hover {
    transform: translateY(-5px);
    border-color: rgba(139, 92, 246, 0.4);
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
}

.project-icon {
    font-size: 2rem;
    color: #8b5cf6;
    margin-bottom: 1.5rem;
}

.project-card h3 {
    font-size: 1.35rem;
    margin-bottom: 0.75rem;
    color: #ffffff;
}

.project-card p {
    color: #94a3b8;
    font-size: 0.95rem;
    margin-bottom: 1.75rem;
}

.project-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
}

.p-tag {
    font-family: 'Fira Code', monospace;
    font-size: 0.75rem;
    color: #06b6d4;
    background: rgba(6, 182, 212, 0.08);
    padding: 2px 8px;
    border-radius: 4px;
}

/* Experience */
.timeline {
    border-left: 2px solid rgba(255, 255, 255, 0.05);
    padding-left: 2rem;
    margin-left: 1rem;
    max-width: 800px;
}

.timeline-item {
    position: relative;
    margin-bottom: 3rem;
}

.timeline-item:last-child {
    margin-bottom: 0;
}

.timeline-dot {
    position: absolute;
    left: -39px;
    top: 6px;
    width: 14px;
    height: 14px;
    background-color: #8b5cf6;
    border: 3px solid #0b0f19;
    border-radius: 50%;
}

.timeline-date {
    font-family: 'Fira Code', monospace;
    font-size: 0.85rem;
    color: #06b6d4;
    margin-bottom: 0.5rem;
}

.timeline-role {
    font-size: 1.25rem;
    color: #ffffff;
}

.timeline-company {
    font-size: 1rem;
    color: #94a3b8;
    margin-bottom: 0.75rem;
}

.timeline-item p {
    font-size: 0.95rem;
    color: #64748b;
}

/* Contact */
.contact-container {
    display: grid;
    grid-template-columns: 1fr 1.2fr;
    gap: 4rem;
}

@media (max-width: 768px) {
    .contact-container {
        grid-template-columns: 1fr;
        gap: 2.5rem;
    }
}

.contact-info p {
    font-size: 1.1rem;
    color: #94a3b8;
    margin-bottom: 2.5rem;
}

.contact-links {
    display: flex;
    flex-direction: column;
    gap: 1.25rem;
}

.contact-links a {
    color: #ffffff;
    text-decoration: none;
    font-family: 'Fira Code', monospace;
    font-size: 0.95rem;
    display: flex;
    align-items: center;
    gap: 12px;
    transition: color 0.3s;
}

.contact-links a:hover {
    color: #06b6d4;
}

.contact-form {
    background-color: #121824;
    border: 1px solid rgba(255, 255, 255, 0.05);
    padding: 2.5rem;
    border-radius: 12px;
    display: flex;
    flex-direction: column;
    gap: 1.25rem;
}

.contact-form input, .contact-form textarea {
    width: 100%;
    padding: 12px 16px;
    background-color: #1a2234;
    border: 1px solid rgba(255, 255, 255, 0.05);
    color: #ffffff;
    border-radius: 6px;
    font-family: inherit;
    outline: none;
    font-size: 0.95rem;
}

.contact-form input:focus, .contact-form textarea:focus {
    border-color: #06b6d4;
}

.contact-form button {
    cursor: pointer;
    align-self: flex-start;
}

footer {
    text-align: center;
    padding: 3rem 0;
    color: #64748b;
    border-top: 1px solid rgba(255, 255, 255, 0.05);
    font-size: 0.9rem;
    font-family: 'Fira Code', monospace;
}
"""

    return {
        "html": html,
        "css": css
    }
