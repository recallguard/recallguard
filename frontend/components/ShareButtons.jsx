import { Twitter, Facebook, Linkedin, Reddit } from 'lucide-react';

export default function ShareButtons({ url, text }) {
  const encodedText = encodeURIComponent(text || '');
  const encodedUrl = encodeURIComponent(url || '');
  return (
    <div style={{ display: 'flex', gap: '0.5em' }}>
      <a
        href={`https://twitter.com/intent/tweet?text=${encodedText}&url=${encodedUrl}`}
        target="_blank"
        rel="noopener noreferrer"
      >
        <Twitter size={20} />
      </a>
      <a
        href={`https://www.facebook.com/sharer/sharer.php?u=${encodedUrl}&quote=${encodedText}`}
        target="_blank"
        rel="noopener noreferrer"
      >
        <Facebook size={20} />
      </a>
      <a
        href={`https://www.linkedin.com/shareArticle?mini=true&url=${encodedUrl}&title=${encodedText}`}
        target="_blank"
        rel="noopener noreferrer"
      >
        <Linkedin size={20} />
      </a>
      <a
        href={`https://www.reddit.com/submit?url=${encodedUrl}&title=${encodedText}`}
        target="_blank"
        rel="noopener noreferrer"
      >
        <Reddit size={20} />
      </a>
    </div>
  );
}
