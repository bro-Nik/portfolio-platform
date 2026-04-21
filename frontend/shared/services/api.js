const errorTranslations = {
  'Field required': 'обязательное поле',
  'Input should be a valid integer': 'должно быть числом',
  'Input should be a valid string': 'должно быть строкой',
  'ensure this value is not empty': 'не должно быть пустым',
};

const translateError = (msg) => errorTranslations[msg] || msg;

export const apiService = (baseUrl = '', getToken, convertCase = false) => {

  const getAuthHeaders = async () => {
    if (!getToken) return {};

    const token = await getToken();
    return token ? { 'Authorization': `Bearer ${token}` } : {};
  };

  const request = async (url, options = {}) => {
    const fullUrl = `${baseUrl}${url}`;
    try {
      const response = await fetch(fullUrl, {
        headers: {
          'Content-Type': 'application/json',
          ... await getAuthHeaders(),
        },
        ...options,
      });

      let data = await response.json().catch(() => null);
      data = snakeToCamel(data);

      if (!response.ok) {
        let message;
        if (data?.detail) {
          if (Array.isArray(data.detail)) {
            message = data.detail.map(d => {
              const field = d.loc?.[1] || d.loc?.[0] || 'поле';
              const msg = translateError(d.msg);
              return `${field}: ${msg}`;
            }).join(', ');
          } else {
            message = data.detail;
          }
        } else if (data?.message) {
          message = data.message;
        } else {
          message = `Ошибка ${response.status}`;
        }
        throw new Error(message);
      }

      console.log('Запрос завершен, ', fullUrl)
      return data;
    } catch (error) {
      console.log('Ошибка запроса, ', fullUrl, error)
      throw error;
    }
  };

  const get = (url) => {
    return request(url);
  };


  const post = (url, body) => {
    return request(url, {
      method: 'POST',
      body: JSON.stringify(convertCase ? camelToSnake(body) : body),
    });
  };

  const put = (url, body) => {
    return request(url, {
      method: 'PUT',
      body: JSON.stringify(convertCase ? camelToSnake(body) : body),
    });
  };

  const del = (url) => {
    return request(url, {
      method: 'DELETE',
    });
  };

  return { get, post, put, del };
};

const snakeToCamel = (obj) => {
  if (obj === undefined || obj === null) return obj;

  if (Array.isArray(obj)) {
    return obj.map(v => snakeToCamel(v));
  } else if (obj.constructor === Object) {
    return Object.keys(obj).reduce((result, key) => {
      const camelKey = key.replace(/_([a-z])/g, (_, letter) => letter.toUpperCase());
      result[camelKey] = snakeToCamel(obj[key]);
      return result;
    }, {});
  }
  return obj;
};

const camelToSnake = (obj) => {
  if (obj === undefined || obj === null) return obj;

  if (Array.isArray(obj)) {
    return obj.map(v => camelToSnake(v));
  } else if (obj.constructor === Object) {
    return Object.keys(obj).reduce((result, key) => {
      const snakeKey = key.replace(/([A-Z])/g, (_, letter) => `_${letter.toLowerCase()}`);
      result[snakeKey] = camelToSnake(obj[key]);
      return result;
    }, {});
  }
  return obj;
};
