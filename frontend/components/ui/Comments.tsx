import React, { useState } from 'react';
import { format } from 'date-fns';

interface Comment {
  id: number;
  content: string;
  user_id: string;
  created_at: string;
  updated_at?: string;
  section?: string;
  replies: Comment[];
}

interface CommentsProps {
  comments: Comment[];
  currentSection?: string;
  onAddComment: (content: string, parentId?: number) => Promise<void>;
  onUpdateComment: (commentId: number, content: string) => Promise<void>;
  onDeleteComment: (commentId: number) => Promise<void>;
}

export const Comments: React.FC<CommentsProps> = ({
  comments,
  currentSection,
  onAddComment,
  onUpdateComment,
  onDeleteComment,
}) => {
  const [newComment, setNewComment] = useState('');
  const [replyTo, setReplyTo] = useState<number | null>(null);
  const [editingComment, setEditingComment] = useState<number | null>(null);
  const [editContent, setEditContent] = useState('');

  const handleSubmit = async (e: React.FormEvent, parentId?: number) => {
    e.preventDefault();
    const content = parentId ? editContent : newComment;
    if (!content.trim()) return;

    try {
      await onAddComment(content, parentId);
      if (parentId) {
        setReplyTo(null);
      } else {
        setNewComment('');
      }
    } catch (error) {
      console.error('Failed to add comment:', error);
    }
  };

  const handleUpdate = async (commentId: number) => {
    if (!editContent.trim()) return;

    try {
      await onUpdateComment(commentId, editContent);
      setEditingComment(null);
      setEditContent('');
    } catch (error) {
      console.error('Failed to update comment:', error);
    }
  };

  const renderComment = (comment: Comment, isReply = false) => (
    <div
      key={comment.id}
      className={`p-4 ${isReply ? 'ml-8 mt-2' : 'border-b'} ${
        comment.section === currentSection ? 'bg-blue-50' : ''
      }`}
    >
      {editingComment === comment.id ? (
        <div className="space-y-2">
          <textarea
            value={editContent}
            onChange={(e) => setEditContent(e.target.value)}
            className="w-full p-2 border rounded"
            rows={3}
          />
          <div className="flex space-x-2">
            <button
              onClick={() => handleUpdate(comment.id)}
              className="px-3 py-1 text-sm bg-blue-500 text-white rounded hover:bg-blue-600"
            >
              Salvar
            </button>
            <button
              onClick={() => {
                setEditingComment(null);
                setEditContent('');
              }}
              className="px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded hover:bg-gray-200"
            >
              Cancelar
            </button>
          </div>
        </div>
      ) : (
        <>
          <div className="flex justify-between items-start">
            <div>
              <p className="text-sm text-gray-500">
                {format(new Date(comment.created_at), 'dd/MM/yyyy HH:mm')}
                {comment.section && (
                  <span className="ml-2 text-blue-500">#{comment.section}</span>
                )}
              </p>
              <p className="mt-1">{comment.content}</p>
            </div>
            <div className="flex space-x-2">
              <button
                onClick={() => {
                  setEditingComment(comment.id);
                  setEditContent(comment.content);
                }}
                className="text-sm text-gray-500 hover:text-gray-700"
              >
                Editar
              </button>
              <button
                onClick={() => onDeleteComment(comment.id)}
                className="text-sm text-red-500 hover:text-red-700"
              >
                Excluir
              </button>
              {!isReply && (
                <button
                  onClick={() => setReplyTo(comment.id)}
                  className="text-sm text-gray-500 hover:text-gray-700"
                >
                  Responder
                </button>
              )}
            </div>
          </div>

          {replyTo === comment.id && (
            <form
              onSubmit={(e) => handleSubmit(e, comment.id)}
              className="mt-2 space-y-2"
            >
              <textarea
                value={editContent}
                onChange={(e) => setEditContent(e.target.value)}
                placeholder="Digite sua resposta..."
                className="w-full p-2 border rounded"
                rows={2}
              />
              <div className="flex space-x-2">
                <button
                  type="submit"
                  className="px-3 py-1 text-sm bg-blue-500 text-white rounded hover:bg-blue-600"
                >
                  Responder
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setReplyTo(null);
                    setEditContent('');
                  }}
                  className="px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded hover:bg-gray-200"
                >
                  Cancelar
                </button>
              </div>
            </form>
          )}
        </>
      )}

      {comment.replies?.length > 0 && (
        <div className="mt-2">
          {comment.replies.map((reply) => renderComment(reply, true))}
        </div>
      )}
    </div>
  );

  return (
    <div className="bg-white rounded-lg shadow">
      <div className="p-4 border-b">
        <h3 className="text-lg font-semibold mb-4">Comentários</h3>
        <form onSubmit={handleSubmit} className="space-y-2">
          <textarea
            value={newComment}
            onChange={(e) => setNewComment(e.target.value)}
            placeholder="Adicione um comentário..."
            className="w-full p-2 border rounded"
            rows={3}
          />
          <button
            type="submit"
            className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
          >
            Comentar
          </button>
        </form>
      </div>

      <div className="divide-y">
        {comments.map((comment) => renderComment(comment))}
      </div>
    </div>
  );
};
