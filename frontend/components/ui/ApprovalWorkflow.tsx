import React, { useState } from 'react';
import { format } from 'date-fns';

interface User {
  id: number;
  username: string;
  full_name: string;
}

interface ReviewStatus {
  status: string;
  metadata: {
    review_submitted_by: number;
    review_submitted_at: string;
    reviewers: number[];
    approvals: Array<{
      reviewer_id: number;
      decision: string;
      comments: string;
      timestamp: string;
    }>;
    rejections: Array<{
      reviewer_id: number;
      decision: string;
      comments: string;
      timestamp: string;
    }>;
    review_comments: string[];
  };
  approvals: number;
  rejections: number;
  pending: number;
}

interface ApprovalWorkflowProps {
  proposalId: number;
  status: ReviewStatus;
  availableReviewers: User[];
  currentUser: User;
  onSubmitForReview: (reviewers: number[]) => Promise<void>;
  onReviewProposal: (approved: boolean, comments: string) => Promise<void>;
  onCancelReview: () => Promise<void>;
}

export const ApprovalWorkflow: React.FC<ApprovalWorkflowProps> = ({
  proposalId,
  status,
  availableReviewers,
  currentUser,
  onSubmitForReview,
  onReviewProposal,
  onCancelReview,
}) => {
  const [selectedReviewers, setSelectedReviewers] = useState<number[]>([]);
  const [reviewComment, setReviewComment] = useState('');
  const [showReviewForm, setShowReviewForm] = useState(false);

  const isReviewer = status.metadata?.reviewers?.includes(currentUser.id);
  const hasReviewed = [...(status.metadata?.approvals || []), ...(status.metadata?.rejections || [])]
    .some(review => review.reviewer_id === currentUser.id);

  const handleSubmitForReview = async () => {
    if (selectedReviewers.length === 0) return;
    try {
      await onSubmitForReview(selectedReviewers);
      setSelectedReviewers([]);
    } catch (error) {
      console.error('Failed to submit for review:', error);
    }
  };

  const handleReview = async (approved: boolean) => {
    if (!reviewComment.trim()) return;
    try {
      await onReviewProposal(approved, reviewComment);
      setReviewComment('');
      setShowReviewForm(false);
    } catch (error) {
      console.error('Failed to submit review:', error);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow p-4">
      <h3 className="text-lg font-semibold mb-4">Fluxo de Aprovação</h3>

      {status.status === 'draft' && (
        <div className="space-y-4">
          <h4 className="font-medium">Enviar para Aprovação</h4>
          <div className="space-y-2">
            <label className="block text-sm font-medium text-gray-700">
              Selecione os Revisores
            </label>
            <div className="grid grid-cols-2 gap-2">
              {availableReviewers.map((reviewer) => (
                <label
                  key={reviewer.id}
                  className="flex items-center space-x-2 p-2 border rounded hover:bg-gray-50"
                >
                  <input
                    type="checkbox"
                    checked={selectedReviewers.includes(reviewer.id)}
                    onChange={() => {
                      if (selectedReviewers.includes(reviewer.id)) {
                        setSelectedReviewers(selectedReviewers.filter(id => id !== reviewer.id));
                      } else {
                        setSelectedReviewers([...selectedReviewers, reviewer.id]);
                      }
                    }}
                    className="rounded text-blue-500"
                  />
                  <span>{reviewer.full_name}</span>
                </label>
              ))}
            </div>
            <button
              onClick={handleSubmitForReview}
              disabled={selectedReviewers.length === 0}
              className="mt-4 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:bg-gray-300"
            >
              Enviar para Aprovação
            </button>
          </div>
        </div>
      )}

      {status.status === 'review' && (
        <div className="space-y-4">
          <div className="flex justify-between items-center">
            <h4 className="font-medium">Em Revisão</h4>
            {status.metadata?.review_submitted_by === currentUser.id && (
              <button
                onClick={onCancelReview}
                className="px-3 py-1 text-sm text-red-500 border border-red-500 rounded hover:bg-red-50"
              >
                Cancelar Revisão
              </button>
            )}
          </div>

          <div className="grid grid-cols-3 gap-4 text-center">
            <div className="p-3 bg-green-50 rounded">
              <div className="text-2xl font-bold text-green-600">{status.approvals}</div>
              <div className="text-sm text-gray-600">Aprovações</div>
            </div>
            <div className="p-3 bg-red-50 rounded">
              <div className="text-2xl font-bold text-red-600">{status.rejections}</div>
              <div className="text-sm text-gray-600">Rejeições</div>
            </div>
            <div className="p-3 bg-gray-50 rounded">
              <div className="text-2xl font-bold text-gray-600">{status.pending}</div>
              <div className="text-sm text-gray-600">Pendentes</div>
            </div>
          </div>

          {isReviewer && !hasReviewed && (
            <div className="mt-4">
              {showReviewForm ? (
                <div className="space-y-4">
                  <textarea
                    value={reviewComment}
                    onChange={(e) => setReviewComment(e.target.value)}
                    placeholder="Digite seus comentários..."
                    className="w-full p-2 border rounded"
                    rows={4}
                  />
                  <div className="flex space-x-2">
                    <button
                      onClick={() => handleReview(true)}
                      className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600"
                    >
                      Aprovar
                    </button>
                    <button
                      onClick={() => handleReview(false)}
                      className="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600"
                    >
                      Rejeitar
                    </button>
                    <button
                      onClick={() => setShowReviewForm(false)}
                      className="px-4 py-2 bg-gray-100 text-gray-700 rounded hover:bg-gray-200"
                    >
                      Cancelar
                    </button>
                  </div>
                </div>
              ) : (
                <button
                  onClick={() => setShowReviewForm(true)}
                  className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
                >
                  Avaliar Proposta
                </button>
              )}
            </div>
          )}

          <div className="mt-4 space-y-2">
            <h5 className="font-medium">Histórico de Revisões</h5>
            {[...(status.metadata?.approvals || []), ...(status.metadata?.rejections || [])]
              .sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())
              .map((review, index) => (
                <div
                  key={index}
                  className={`p-3 rounded ${
                    review.decision === 'approved' ? 'bg-green-50' : 'bg-red-50'
                  }`}
                >
                  <div className="flex justify-between text-sm">
                    <span className={review.decision === 'approved' ? 'text-green-600' : 'text-red-600'}>
                      {review.decision === 'approved' ? 'Aprovado' : 'Rejeitado'}
                    </span>
                    <span className="text-gray-500">
                      {format(new Date(review.timestamp), 'dd/MM/yyyy HH:mm')}
                    </span>
                  </div>
                  {review.comments && (
                    <p className="mt-1 text-sm text-gray-600">{review.comments}</p>
                  )}
                </div>
              ))}
          </div>
        </div>
      )}

      {status.status === 'approved' && (
        <div className="text-center p-6 bg-green-50 rounded">
          <div className="text-xl font-semibold text-green-600 mb-2">
            Proposta Aprovada
          </div>
          <p className="text-sm text-gray-600">
            Todas as aprovações necessárias foram obtidas.
          </p>
        </div>
      )}
    </div>
  );
};
