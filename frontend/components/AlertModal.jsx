import ShareButtons from './ShareButtons.jsx';

export default function AlertModal({ message, recall }) {
  const text = recall
    ? `Recall alert: ${recall.product_name || recall.product} – stay safe with RecallHero`
    : 'Stay safe with RecallHero';
  const url = `${process.env.NEXT_PUBLIC_FRONTEND_ORIGIN}/signup?src=share`;
  return (
    <div>
      {message}
      <ShareButtons url={url} text={text} />
    </div>
  );
}

